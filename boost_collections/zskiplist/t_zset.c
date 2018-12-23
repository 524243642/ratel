#include <Python.h>
#include "structmember.h"

#define LESSTHAN(p, q) PyObject_RichCompareBool(p, q, Py_LT)
#define EQUAL(p, q)    PyObject_RichCompareBool(p, q, Py_EQ)


#if PY_MAJOR_VERSION >= 3
#define PY3
#define AS_STR PyUnicode_AsUTF8
#define STR_FROM_FORMAT PyUnicode_FromFormat
#else
#define AS_STR PyString_AsString
#define STR_FROM_FORMAT PyString_FromFormat
#endif

#define SUC Py_BuildValue("i", 1)
#define FIL Py_BuildValue("i", 0)

#define ZSKIPLIST_MAXLEVEL 32
#define ZSKIPLIST_P 0.25

typedef struct zskiplistNode {
    PyObject *ele;
    double score;
    struct zskiplistNode *backward;
    struct zskiplistLevel {
        struct zskiplistNode *forward;
        unsigned long span;
    } level[];
} zskiplistNode;

typedef struct {
    PyObject_HEAD
    struct zskiplistNode *header, *tail;
    unsigned long length;
    int level;
} zskiplist;

static int zslRandomLevel(void) {
    int level = 1;
    while ((random()&0xFFFF) < (ZSKIPLIST_P * 0xFFFF))
        level += 1;
    return (level<ZSKIPLIST_MAXLEVEL) ? level : ZSKIPLIST_MAXLEVEL;
}

static char *
cstr_repr(PyObject *o)
{
    PyObject *r;
    char *s;

    r = PyObject_Repr(o);
    if (r == NULL)
        return NULL;

    s = AS_STR(r);
    Py_DECREF(r);
    return s;
}

static zskiplistNode *zslCreateNode(int level, double score, PyObject *ele) {
    int size = sizeof(zskiplistNode)+level*sizeof(struct zskiplistLevel);
    zskiplistNode *zn = PyMem_Malloc(size);
    if (!zn)
        return NULL;
    memset(zn, '\0', size);
    zn->score = score;
    zn->ele = ele;
    if(ele!=NULL)
        Py_INCREF(ele);
    return zn;
}

static PyObject *zslInsert(zskiplist *zsl, PyObject *args) {

    double score;
    PyObject *ele;


    if(!PyArg_ParseTuple(args, "d|O", &score, &ele)){
        return FIL;
    }

    if (PyErr_Occurred())
        return FIL;
    zskiplistNode *update[ZSKIPLIST_MAXLEVEL], *x;
    unsigned int rank[ZSKIPLIST_MAXLEVEL];
    int i, level;
    x = zsl->header;
    int cmp;

    assert(!isnan(score));
    for (i = zsl->level-1; i >= 0; i--) {
        rank[i] = i == (zsl->level-1) ? 0 : rank[i+1];
        while (x->level[i].forward &&
                (x->level[i].forward->score < score ||
                    (x->level[i].forward->score == score &&
                    (cmp=LESSTHAN(x->level[i].forward->ele,ele)))))
        {
            if (cmp==-1)
                return FIL;
            rank[i] += x->level[i].span;
            x = x->level[i].forward;
        }
        update[i] = x;
    }
    if (PyErr_Occurred())
        return FIL;
    level = zslRandomLevel();
    if (level > zsl->level) {
        for (i = zsl->level; i < level; i++) {
            rank[i] = 0;
            update[i] = zsl->header;
            update[i]->level[i].span = zsl->length;
        }
        zsl->level = level;
    }
    x = zslCreateNode(level,score,ele);
    if (x == NULL)
        return PyErr_NoMemory();
    for (i = 0; i < level; i++) {
        x->level[i].forward = update[i]->level[i].forward;
        update[i]->level[i].forward = x;
        x->level[i].span = update[i]->level[i].span - (rank[0] - rank[i]);
        update[i]->level[i].span = (rank[0] - rank[i]) + 1;
    }
    for (i = level; i < zsl->level; i++) {
        update[i]->level[i].span++;
    }

    x->backward = (update[0] == zsl->header) ? NULL : update[0];
    if (x->level[0].forward)
        x->level[0].forward->backward = x;
    else
        zsl->tail = x;
    zsl->length++;
    return SUC;
}

static void zslDeleteNode(zskiplist *zsl, zskiplistNode *x, zskiplistNode **update) {
    int i;
    for (i = 0; i < zsl->level; i++) {
        if (update[i]->level[i].forward == x) {
            update[i]->level[i].span += x->level[i].span - 1;
            update[i]->level[i].forward = x->level[i].forward;
        } else {
            update[i]->level[i].span -= 1;
        }
    }
    if (x->level[0].forward) {
        x->level[0].forward->backward = x->backward;
    } else {
        zsl->tail = x->backward;
    }
    while(zsl->level > 1 && zsl->header->level[zsl->level-1].forward == NULL)
        zsl->level--;
    zsl->length--;
}

static void zslFreeNode(zskiplistNode *node) {
    Py_DECREF(node->ele);
    PyMem_Free(node);
}

static void zslFree(zskiplist *zsl) {
    zskiplistNode *node = zsl->header->level[0].forward, *next;

    PyMem_Free(zsl->header);
    while(node) {
        next = node->level[0].forward;
        Py_XDECREF(node->ele);
        PyMem_FREE(node);
        node = next;
    }
//    PyMem_Free(zsl);
}

static PyObject *zslDelete(zskiplist *zsl, PyObject *args) {
    double score;
    PyObject *ele;


    if(!PyArg_ParseTuple(args, "d|O", &score, &ele)){
        return FIL;
    }

    if (PyErr_Occurred())
        return FIL;

    zskiplistNode *update[ZSKIPLIST_MAXLEVEL], *x;
    int i;
    int cmp;
    x = zsl->header;
    for (i = zsl->level-1; i >= 0; i--) {
        while (x->level[i].forward &&
                (x->level[i].forward->score < score ||
                    (x->level[i].forward->score == score &&
                     (cmp=LESSTHAN(x->level[i].forward->ele,ele)))))
        {
            if (cmp==-1)
                return Py_BuildValue("i", 0);
            x = x->level[i].forward;
        }
        update[i] = x;
    }
    x = x->level[0].forward;
    if (x && score == x->score && EQUAL(x->ele,ele)) {
        zslDeleteNode(zsl, x, update);
        zslFreeNode(x);
        return SUC;
    }
    return FIL;
}

static zskiplistNode* zslGetElementByRank(zskiplist *zsl, unsigned long rank) {
    zskiplistNode *x;
    unsigned long traversed = 0;
    int i;
    x = zsl->header;
    for (i = zsl->level-1; i >= 0; i--) {
        while (x->level[i].forward && (traversed + x->level[i].span) <= rank)
        {
            traversed += x->level[i].span;
            x = x->level[i].forward;
        }
        if (traversed == rank) {
            return x;
        }
    }
    return NULL;
}

static PyObject* zslGetLowerElementByScore(zskiplist *zsl, PyObject *args) {
    double score;
    if(!PyArg_ParseTuple(args, "d", &score)){
        return FIL;
    }

    if (PyErr_Occurred())
        return FIL;

    zskiplistNode *x;
    int i;
    x = zsl->header;
    for (i = zsl->level-1; i >= 0; i--) {
        while (x->level[i].forward && x->level[i].forward->score < score)
        {
            x = x->level[i].forward;
        }
    }
    if (x != zsl->header) {
        PyObject* ele = x->ele;
        PyObject* pObj = PyTuple_New(2);
        PyTuple_SetItem(pObj, 0, ele);
        Py_INCREF(ele);
        PyTuple_SetItem(pObj, 1, Py_BuildValue("f", x->score));
        return pObj;
    }
    Py_RETURN_NONE;
}

static PyObject* zslGetFloorElementByScore(zskiplist *zsl, PyObject *args) {
    double score;
    if(!PyArg_ParseTuple(args, "d", &score)){
        return FIL;
    }

    if (PyErr_Occurred())
        return FIL;

    zskiplistNode *x;
    int i;
    x = zsl->header;
    for (i = zsl->level-1; i >= 0; i--) {
        while (x->level[i].forward && x->level[i].forward->score <= score)
        {
            x = x->level[i].forward;
        }
    }
    if (x != zsl->header) {
        PyObject* ele = x->ele;
        PyObject* pObj = PyTuple_New(2);
        PyTuple_SetItem(pObj, 0, ele);
        Py_INCREF(ele);
        PyTuple_SetItem(pObj, 1, Py_BuildValue("f", x->score));
        return pObj;
    }
    Py_RETURN_NONE;
}

static PyObject* zslRangeGeneric(zskiplist *zsl, PyObject *args) {

    long reverse;
    long start;
    long rangelen;
    unsigned long llen = zsl->length;

    if(!PyArg_ParseTuple(args, "l|l|l", &reverse, &start, &rangelen)){
        return PyList_New(0);
    }

    zskiplistNode *ln;
    PyObject* pList = PyList_New(rangelen);
    long i;
    if (reverse) {
        ln = zsl->tail;
        if (start > 0)
            ln = zslGetElementByRank(zsl,llen-start);
    } else {
        ln = zsl->header->level[0].forward;
        if (start > 0)
            ln = zslGetElementByRank(zsl,start+1);
    }

    for (i = 0; i < rangelen; i++) {
        PyObject* ele = ln->ele;
        PyObject* pObj = PyTuple_New(2);
        PyTuple_SetItem(pObj, 0, ele);
        Py_INCREF(ele);
        PyTuple_SetItem(pObj, 1, Py_BuildValue("f", ln->score));
        PyList_SetItem(pList, i, pObj);
        ln = reverse ? ln->backward : ln->level[0].forward;
    }
    return pList;
}

static PyObject *
zskiplist_alloc(PyTypeObject *type)
{
    zskiplist *zsl = NULL;

    zsl = (zskiplist *)type->tp_alloc(type, 0);
    if (zsl == NULL)
        return NULL;
    int j;
    zsl->level = 1;
    zsl->length = 0;
    zsl->header = zslCreateNode(ZSKIPLIST_MAXLEVEL,0,NULL);
    for (j = 0; j < ZSKIPLIST_MAXLEVEL; j++) {
        zsl->header->level[j].forward = NULL;
        zsl->header->level[j].span = 0;
    }
    zsl->header->backward = NULL;
    zsl->tail = NULL;
    return (PyObject *)zsl;
}

static void
zskiplist_dealloc(zskiplist *zsl)
{
    zslFree(zsl);
    PyObject_GC_Del((PyObject *)zsl);
}

static PyObject *
zskiplist_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return zskiplist_alloc(type);
}

static int
zskiplist_init(zskiplist *zsl, PyObject *args, PyObject *kwds)
{
    return 0;
}

static int
zskiplist_traverse(zskiplist *zsl, visitproc visit, void *arg)
{

    zskiplistNode *node = zsl->header->level[0].forward, *next;

    while(node) {
        next = node->level[0].forward;
        Py_VISIT(node->ele);
        node = next;
    }
    return 0;
}

static Py_ssize_t
zskiplist_length(zskiplist *zsl)
{
    return zsl->length;
}

static PyObject *
zskiplist_repr(zskiplist *zsl)
{
    PyObject *result = NULL, *keys;
    char *listrepr;
    int status = Py_ReprEnter((PyObject*)zsl);

    if (status != 0) {
        if (status < 0)
            return NULL;
        return STR_FROM_FORMAT("%s(...)", Py_TYPE(zsl)->tp_name);
    }

    if (!zsl->length) {
        Py_ReprLeave((PyObject*)zsl);
        return STR_FROM_FORMAT("%s()", Py_TYPE(zsl)->tp_name);
    }

    keys = PySequence_List((PyObject*)zsl);
    if (keys == NULL)
        goto done;

    listrepr = cstr_repr(keys);
    Py_DECREF(keys);
    if (listrepr == NULL)
        goto done;

    listrepr = strdup(listrepr);
    result = STR_FROM_FORMAT("%s(%s)", Py_TYPE(zsl)->tp_name, listrepr);
    free(listrepr);

done:
    Py_ReprLeave((PyObject*)zsl);
    return result;
}

PyDoc_STRVAR(zslInsert_doc,
"S.zslInsert(score,ele) -> None -- Add element elem to the skiplist.");

PyDoc_STRVAR(zslDelete_doc,
"S.zslDelete(score,ele) -> int -- Remove element from the skiplist if it is present.");

PyDoc_STRVAR(zslRangeGeneric_doc,
"S.zslRangeGeneric(reverse,start,rangelen) -> list -- Get elements by condition.");

PyDoc_STRVAR(zslGetFloorElementByScore_doc,
"S.zslGetFloorElementByScore(score) -> tuple -- Returns a key-value mapping associated with the greatest score less than or equal to the given score.");

PyDoc_STRVAR(zslGetLowerElementByScore_doc,
"S.zslGetLowerElementByScore(score) -> tuple -- Returns a key-value mapping associated with the greatest score less than the given score.");

static PyMethodDef zskiplist_methods[] = {
    {"zslInsert", (PyCFunction)zslInsert, METH_VARARGS, zslInsert_doc},
    {"zslDelete", (PyCFunction)zslDelete, METH_VARARGS, zslDelete_doc},
    {"zslRangeGeneric", (PyCFunction)zslRangeGeneric, METH_VARARGS, zslRangeGeneric_doc},
    {"zslGetFloorElementByScore", (PyCFunction)zslGetFloorElementByScore, METH_VARARGS, zslGetFloorElementByScore_doc},
    {"zslGetLowerElementByScore", (PyCFunction)zslGetLowerElementByScore, METH_VARARGS, zslGetLowerElementByScore_doc},
    {NULL}  /* Sentinel */
};

static PySequenceMethods zskiplist_as_sequence = {
    (lenfunc)zskiplist_length,      /* sq_length */
    0,                              /* sq_concat */
    0,                              /* sq_repeat */
    0,                              /* sq_item */
    0,                              /* sq_slice */
    0,                              /* sq_ass_item */
    0,                              /* sq_ass_slice */
    0,                              /* sq_contains */
    0,                              /* sq_inplace_concat */
    0,                              /* sq_inplace_repeat */
};

static PyTypeObject zskiplistType = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "zskiplist",                   /* tp_name */
    sizeof(zskiplist),             /* tp_basicsize */
    0,                             /* tp_itemsize */
    (destructor)zskiplist_dealloc, /* tp_dealloc */
    0,                             /* tp_print */
    0,                             /* tp_getattr */
    0,                             /* tp_setattr */
    0,                             /* tp_reserved */
    (reprfunc)zskiplist_repr,      /* tp_repr */
    0,                             /* tp_as_number */
    &zskiplist_as_sequence,        /* tp_as_sequence */
    0,                             /* tp_as_mapping */
    PyObject_HashNotImplemented,   /* tp_hash  */
    0,                             /* tp_call */
    0,                             /* tp_str */
    0,                             /* tp_getattro */
    0,                             /* tp_setattro */
    0,                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /* tp_flags */
    "zskiplist Objects",           /* tp_doc */
    (traverseproc)zskiplist_traverse,     /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    zskiplist_methods,             /* tp_methods */
    0,                             /* tp_members */
    0,                             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)zskiplist_init,      /* tp_init */
    PyType_GenericAlloc,           /* tp_alloc */
    zskiplist_new,                 /* tp_new */
};


#ifdef PY3

#define INITERROR return NULL
#define INIT PyMODINIT_FUNC PyInit__zskiplist

static PyModuleDef zskiplistmodule = {
    PyModuleDef_HEAD_INIT,
    "_zskiplist",
    "SkipList implementation",
    -1
};

#else

#define INITERROR return
#define INIT void init_zskiplist

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#endif


INIT(void)
{
    PyObject *m;

    if (PyType_Ready(&zskiplistType) < 0)
        INITERROR;

#ifdef PY3
    m = PyModule_Create(&zskiplistmodule);
#else
    m = Py_InitModule("_zskiplist", module_methods);
#endif
    if (m == NULL)
        INITERROR;

    Py_INCREF(&zskiplistType);
    PyModule_AddObject(m, "zskiplist", (PyObject *)&zskiplistType);

#ifdef PY3
    return m;
#endif
}







