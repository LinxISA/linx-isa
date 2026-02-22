'use strict';

const tspan = require('tspan');

const drawGate = require('./draw_gate.js');

function drawBoxes (tree, xmax) {
  const ret = ['g'];
  const spec = [];
  if (Array.isArray(tree)) {
    spec.push(tree[0].name);
    spec.push([32 * (xmax - tree[0].x), 8 * tree[0].y]);

    for (let i = 1; i < tree.length; i++) {
      const branch = tree[i];
      if (Array.isArray(branch)) {
        spec.push([32 * (xmax - branch[0].x), 8 * branch[0].y]);
      } else {
        spec.push([32 * (xmax - branch.x), 8 * branch.y]);
      }
    }
    ret.push(drawGate(spec));
    for (let i = 1; i < tree.length; i++) {
      const branch = tree[i];
      ret.push(drawBoxes(branch, xmax));
    }
    return ret;
  }

  const fname = tree.name;
  const fx = 32 * (xmax - tree.x);
  const fy = 8 * tree.y;
  ret.push(
    ['g', {transform: 'translate(' + fx + ',' + fy + ')'},
      ['title'].concat(tspan.parse(fname)),
      ['path', {d:'M 2,0 a 2,2 0 1 1 -4,0 2,2 0 1 1 4,0 z'}],
      ['text', {x:-4, y:4, class:'pinname'}]
        .concat(tspan.parse(fname))
    ]
  );
  return ret;
}

module.exports = drawBoxes;
