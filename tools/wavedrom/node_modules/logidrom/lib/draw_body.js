'use strict';

const tspan = require('tspan');

const circle = 'M 4,0 C 4,1.1 3.1,2 2,2 0.9,2 0,1.1 0,0 c 0,-1.1 0.9,-2 2,-2 1.1,0 2,0.9 2,2 z';
const buf1 = 'M -11,-6 -11,6 0,0 z m -5,6 5,0';
const and2 = 'm -16,-10 5,0 c 6,0 11,4 11,10 0,6 -5,10 -11,10 l -5,0 z';
const or2 = 'm -18,-10 4,0 c 6,0 12,5 14,10 -2,5 -8,10 -14,10 l -4,0 c 2.5,-5 2.5,-15 0,-20 z';
const xor2 = 'm -21,-10 c 1,3 2,6 2,10 m 0,0 c 0,4 -1,7 -2,10 m 3,-20 4,0 c 6,0 12,5 14,10 -2,5 -8,10 -14,10 l -4,0 c 1,-3 2,-6 2,-10 0,-4 -1,-7 -2,-10 z';
const circle2 = 'c 0,4.418278 -3.581722,8 -8,8 -4.418278,0 -8,-3.581722 -8,-8 0,-4.418278 3.581722,-8 8,-8 4.418278,0 8,3.581722 8,8 z';

const gates = {
  '=': buf1, '~':  buf1 + circle,
  '&': and2, '~&': and2 + circle,
  '|': or2,  '~|': or2  + circle,
  '^': xor2, '~^': xor2 + circle,
  '+': 'm -8,5 0,-10 m -5,5 10,0 m 3,0' + circle2,
  '*': 'm -4,4 -8,-8 m 0,8 8,-8  m 4,4' + circle2,
  '-': 'm -3,0 -10,0 m 13,0' + circle2
};


const aliasGates = {
  add: '+', mul: '*', sub: '-',
  and: '&', or: '|', xor: '^',
  andr: '&', orr: '|', xorr: '^',
  input: '='
};

Object.keys(aliasGates).reduce((res, key) => {
  res[key] = gates[aliasGates[key]];
  return res;
}, gates);

const gater1 = {
  is:     type => (gates[type] !== undefined),
  render: type => ['path', {class:'gate', d: gates[type]}]
};

const iec = {
  eq: '==', ne: '!=',
  slt: '<', sle: '<=',
  sgt: '>', sge: '>=',
  ult: '<', ule: '<=',
  ugt: '>', uge: '>=',
  BUF: 1, INV: 1, AND: '&', NAND: '&',
  OR: '\u22651', NOR: '\u22651', XOR: '=1', XNOR: '=1',
  box: '', MUX: 'M'
};

const circled = {INV: 1, NAND: 1, NOR: 1, XNOR: 1};

const gater2 = {
  is:      type => (iec[type] !== undefined),
  render: (type, ymin, ymax) => {
    if (ymin === ymax) {
      ymin = -4; ymax = 4;
    }
    return ['g',
      ['path', {
        class: 'gate',
        d: 'm -16,' + (ymin - 3) + ' 16,0 0,' + (ymax - ymin + 6) + ' -16,0 z' + (circled[type] ? circle : '')
      }],
      ['text', {x:-14, y:4, class: 'wirename'}].concat(tspan.parse(iec[type]))
    ];
  }
};

function drawBody (type, ymin, ymax) {
  if (gater1.is(type)) { return gater1.render(type); }
  if (gater2.is(type)) { return gater2.render(type, ymin, ymax); }
  return ['text', {x:-14, y:4, class: 'wirename'}].concat(tspan.parse(type));
}

module.exports = drawBody;
