'use strict';

function skipFn() {
  this._skip = true;
}

function removeFn() {
  this._remove = true;
}

function nameFn(name) {
  this._name = name;
}

function replaceFn(node) {
  this._replace = node;
}

function traverse(origin, callbacks) {
  const empty = function() {};

  const enter = callbacks && callbacks.enter || empty;
  const leave = callbacks && callbacks.leave || empty;


  function rec(tree, parent) {
    if (tree === undefined) return;
    if (tree === null) return;
    if (tree === true) return;
    if (tree === false) return;

    const node = {
      attr: {},
      full: tree
    };

    const cxt = {
      name: nameFn,
      skip: skipFn,
      // break: breakFn,
      remove: removeFn,
      replace: replaceFn,

      _name: undefined,
      _skip: false,
      // _break: false,
      _remove: false,
      _replace: undefined
    };

    let e1IsNotAnObject = true;

    switch (Object.prototype.toString.call(tree)) {
    case '[object String]':
    case '[object Number]':
      return;

    case '[object Array]':
      tree.some(function(e, i) {
        if (i === 0) {
          node.name = e;
          return false;
        }
        if (i === 1) {
          if (
            Object.prototype.toString.call(e) === '[object Object]'
          ) {
            e1IsNotAnObject = false;
            node.attr = e;
          }
          return true;
        }
      });

      enter.call(cxt, node, parent);

      if (cxt._name) {
        tree[0] = cxt._name;
      }

      if (cxt._replace) {
        return cxt._replace;
      }

      if (cxt._remove) {
        return null;
      }

      if (!cxt._skip) {
        let index = 0;
        let ilen = tree.length;
        while (index < ilen) {
          if ((index > 1) || ((index === 1) && e1IsNotAnObject)) {
            const returnRes = rec(tree[index], node);
            if (returnRes === null) {
              tree.splice(index, 1);
              ilen -= 1;
              continue;
            }
            if (returnRes) {
              tree[index] = returnRes;
            }
          }
          index += 1;
        }

        leave.call(cxt, node, parent);
        if (cxt._name) {
          tree[0] = cxt._name;
        }
        if (cxt._replace) {
          return cxt._replace;
        }
        if (cxt._remove) {
          return null;
        }
      }
    }
  }

  rec(origin, undefined);
}

module.exports = traverse;

/* eslint complexity: 0 */
