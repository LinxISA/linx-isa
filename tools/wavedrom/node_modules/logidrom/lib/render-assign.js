'use strict';

const render = require('./render.js');
const drawBoxes = require('./draw_boxes.js');
const insertSVGTemplateAssign = require('./insert-svg-template-assign.js');

function renderAssign (index, source) {
  // var tree,
  //     state,
  //     xmax,
  //     // grid = ['g'],
  //     // svgcontent,
  //     width,
  //     height,
  //     i,
  //     ilen;
  //     // j,
  //     // jlen;

  let state = {x: 0, y: 2, xmax: 0};
  const tree = source.assign;
  const ilen = tree.length;
  for (let i = 0; i < ilen; i++) {
    state = render(tree[i], state);
    state.x++;
  }
  const xmax = state.xmax + 3;

  const svg = ['g'];
  for (let i = 0; i < ilen; i++) {
    svg.push(drawBoxes(tree[i], xmax));
  }
  const width  = 32 * (xmax + 1) + 1;
  const height = 8 * (state.y + 1) - 7;

  // const ilen = 4 * (xmax + 1);
  // jlen = state.y + 1;
  // for (i = 0; i <= ilen; i++) {
  //     for (j = 0; j <= jlen; j++) {
  //         grid.push(['rect', {
  //             height: 1,
  //             width: 1,
  //             x: (i * 8 - 0.5),
  //             y: (j * 8 - 0.5),
  //             class: 'grid'
  //         }]);
  //     }
  // }

  return ['svg', {
    id: 'svgcontent_' + index,
    viewBox: '0 0 ' + width + ' ' + height,
    width: width,
    height: height
  },
  insertSVGTemplateAssign(),
  ['g', {transform:'translate(0.5, 0.5)'}, svg]
  ];
}

module.exports = renderAssign;

/* eslint-env browser */
