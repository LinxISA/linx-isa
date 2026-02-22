'use strict';

const parse = require('./parse.js');
const stringify = require('./stringify.js');
const traverse = require('./traverse.js');
const renderer = require('./renderer.js');
const tt = require('./tt.js');
const genSvg = require('./gen-svg.js');

exports.renderer = renderer;
exports.parse = parse;
exports.stringify = stringify;
exports.traverse = traverse;
exports.tt = tt;

exports.gen = {
  svg: genSvg
};

exports.p = parse;
exports.s = stringify;
exports.t = traverse;
