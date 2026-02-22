'use strict';

const genSvg = require('onml/gen-svg.js');

const forest = require('./fir-forest.js');

const render = circuit => {
  const body = forest(circuit);
  const {w, h} = body[1];
  return genSvg(w, h).concat([body]);
};

module.exports = render;
