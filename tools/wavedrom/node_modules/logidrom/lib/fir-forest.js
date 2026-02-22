'use strict';

const tt = require('onml/tt.js');
const {B612} = require('./B612.js');

const f = B612()(16);

const grid = 32;

const ceil = (n, step) => step * Math.ceil(n / step);

const widther = w => (w === 0) ? 'zeroer' : (w === 1) ? 'scalar' : 'vector';

const signed = node => (node.signed ? '' : 'un') + 'signed';

const siglabel = node => (node.signed ? '' : 'un') + 'siglabel';

const symbols = {
  andr: '&', orr: '≥1', xorr: '=1',
  neg: 'neg', not: 'not',

  add:  '+', sub:  '-',
  mul:  '*', div:  '/',      rem:  '%',
  lt: '<', leq: '≤', gt: '>', geq: '≥', eq: '=', neq: '≠',
  dshl: '<<', dshr: '>>',
  and:  '&', or:  '≥1', xor:  '=1',
  cat: '}',
  validif: 'vif'
};

const renderLiteral = (node, ch) => {
  const label = node.value.toString();
  const w = ceil(f.getWidth(label) + 5, grid);
  const h = Math.max(ch, grid);
  const res = ['g', {w, h, id: 'literal'},
    ['title', {}, node.width],
    ['rect', {class: 'literal', width: w - 4, height: h - 4, x: 2, y: -h / 2 + 2}],
    ['text', {
      class: siglabel(node),
      x: w / 2,
      y: 5
    }, label]
  ];
  return res;
};


const renderParameter = (node, ch) => {
  const label = node.name.toString();
  const w = ceil(f.getWidth(label) + 5, grid);
  const h = Math.max(ch, grid);
  const res = ['g', {w, h},
    ['rect', {class: 'literal', width: w - 4, height: h - 4, x: 2, y: -h / 2 + 2}],
    ['text', {class: 'parameter', x: w / 2, y: 5}, label]
  ];
  return res;
};



const renderWire = (node, ch, reuse) => {
  const label = node.name;
  const w = ceil(f.getWidth(label), grid);
  const k = (f.getHeight() / 2 + 1) |0;
  const h = Math.max(ch, 2 * k + 8);
  const res = ['g', {w, h}]
    .concat(
      reuse ? [] : [['path', {
        class: 'mark ' + signed(node),
        d: ['M', 0, -k, 'l', w, 0, 'l', 0, 2 * k, 'l', -w, 0, 'z']
      }]],
      [['text', {
        class: siglabel(node),
        x: w / 2,
        y: k - 4
      }, node.name]]
    );
  return res;
};

const regShapeD = (hbox, wbox, reset) => [
  'm', 0, hbox / 2 - 2,
  'v', 4 - hbox
].concat(
  reset ? [
    'h', wbox / 2 - 4,
    'a', 4, 4, 0, 0, 0, 8, 0,
    'h', wbox / 2 - 4
  ] : [
    'h', wbox
  ],
  [
    'v', hbox - 4,
    'h', 6 - wbox / 2,
    'l', -6, -8, -6, 8,
    'z'
  ]
);

const renderReg = (node, ch, reuse) => {
  const label = node.name;
  const w = ceil(f.getWidth(label), grid);
  const k = (f.getHeight() / 2 + 1) |0;
  const h = Math.max(ch, 2 * k + 8);
  const hbox = Math.min(h, 2 * grid);
  const res = ['g', {w: w + 2 * grid, h}];
  if (!reuse) {
    return res.concat([
      ['path', {
        class: ['dff', signed(node), widther(node.width)],
        d: regShapeD(hbox, grid, (node.type === 'regr'))
      }],
      ['path', {
        class: [signed(node), widther(node.width)],
        d: ['M', grid, 0, 'h', grid, 'm', 0, -k, 'h', w, 'v', 2 * k, 'h', -w, 'z']
      }],
      ['text', {
        class: ['dff', siglabel(node)],
        x: grid / 2,
        y: k - 4
      }, 'ff\u00A0'], // \uFB00
      ['text', {
        class: siglabel(node),
        x: w / 2 + 2 * grid,
        y: k - 4
      }, node.name]
    ]);
  }

  return res.concat([['text', {
    class: siglabel(node),
    x: 2 * grid + w / 2,
    y: k - 4
  }, node.name]]);
};

const renderOutput = (node, ch, reuse) => {
  const label = node.name;
  const w = ceil(f.getWidth(label), grid);
  const k = (f.getHeight() / 2 + 1) |0;
  const h = Math.max(ch, 2 * k + 8);
  const res = ['g', {w, h}]
    .concat(
      reuse ? [] : [['path', {
        class: ['mark', signed(node)],
        d: ['M', 0, -k, 'h', w - k, 'l', k, k, 'l', -k, k, 'h', -(w - k), 'z']
      }]],
      [['text', {
        class: siglabel(node),
        x: w / 2,
        y: k - 4
      }, node.name]]
    );
  return res;
};

const renderInput = (node, ch) => {
  const label = node.name;
  const w = ceil(f.getWidth(label) + 5, grid);
  const k = (f.getHeight() / 2 + 1) |0;
  const h = Math.max(ch, 2 * k + 8);
  const res = ['g', {w, h},
    ['title', {}, node.width],
    ['path', {
      class: ['mark', signed(node), widther(node.width)],
      d: ['M', 0, -h / 2 + 6, 'h', w - k, 'l', k, k, 'l', -k, k, 'h', -(w - k), 'z']
    }],
    ['text', {
      class: siglabel(node),
      x: w / 2,
      y: k - 4
    }, node.name]
  ];
  return res;
};

const buf1 = ['m', 0, -12, 'v', 24, 'l', 22, -12, 'z', 'm', 24, 12];
// const circle = 'c 0,1.8 2.2,4 4,4 c 1.8,0 4,-2.2 4,-4 c 0,-1.8 -2.2,-4 -4,-4 c -1.8,0 -4,2.2 -4,4 z';
const circle = ['a', 4, 4, 0, 1, 1, 0, .01];
// const circle = 'm 0,0 c 0,2.2 -2.2,0 4,4 c 2.2,0 0,2.2 4,-4 c 0,-2.2 0,-2.2 -4,-4 c -2.2,0 0,-2.2 -4,4 z';

const and1 = [
  'm', 0, -10,
  'h', 12,
  'a', 10, 10, 0, 1, 1, 0, 20,
  'h', -12,
  'z',
  'm', 22, 10,
  'h', 10
];

const or1 = [
  'm', -2, 10,
  'a', 22, 22, 0, 0, 0, 0, -20,
  'h', 10,
  'a', 20, 20, 0, 0, 1, 17, 10,
  'a', 20, 20, 0, 0, 1, -17, 10,
  'z',
  'm', 26, -10,
  'h', 8
];

const xor1 = [
  'm', -2, -10,
  'a', 22, 22, 0, 0, 1, 0, 20,
  'm', 4, 0,
  'a', 22, 22, 0, 0, 0, 0, -20,
  'h', 10,
  'a', 22, 22, 0, 0, 1, 16, 10,
  'a', 22, 22, 0, 0, 1, -16, 10,
  'z',
  'm', 25, -10,
  'h', 5
];

const and2 = [
  'm', 0, -20,
  'h', 12,
  'a', 20, 20, 0, 1, 1, 0, 40,
  'h', -12,
  'z'
];

const or2 = [
  'm', -2, 20,
  'a', 40, 40, 0, 0, 0, 0, -40,
  'a', 33, 33, 0, 0, 1, 34, 20,
  'a', 33, 33, 0, 0, 1, -34, 20,
  'z'
];

const xor2 = [
  'm', -2, -20,
  'a', 40, 40, 0, 0, 1, 0, 40,
  'm', 6, 0,
  'a', 40, 40, 0, 0, 0, 0, -40,
  'a', 30, 30, 0, 0, 1, 28, 20,
  'a', 30, 30, 0, 0, 1, -28, 20,
  'z'
];

const circle2 = ['a', 20, 20, 0, 1, 0, 0, .01];

const shapes = {
  not: buf1.concat(circle),
  and: and2,
  or: or2,
  xor: xor2,
  andr: and1,
  orr: or1,
  xorr: xor1,

  add: [
    'm', 12, 10,  'v', -20,
    'm', -10, 10, 'h', 20,
    'm', 10, 0
  ].concat(circle2),

  mul: [
    'm', 20, 8, 'l', -16, -16,
    'm', 0, 16, 'l', 16, -16,
    'm', 12, 8
  ].concat(circle2),

  div: [
    'm', 4, 8, 'l', 16, -16,
    'm', 12, 8
  ].concat(circle2),

  rem: [
    'm', 2, -6, 'a', 4, 4, 0, 1, 1, 0, .01,
    'm', 2, 14, 'l', 16, -16,
    'm', -6, 14, 'a', 4, 4, 0, 1, 1, 0, .01,
    'm', 18, -6
  ].concat(circle2),

  sub: [
    'm', 22, 0, 'h', -20,
    'm', 30, 0
  ].concat(circle2)
};

const renderShape = (node, ch) => {
  const w = grid;
  const h = Math.max(ch, grid);
  const res = ['g', {w, h, class: 'gate'},
    ['title', {}, node.width],
    ['path', {
      class: [signed(node), widther(node.width)],
      d: shapes[node.type]
    }]
  ];
  return res;
};

const renderBox = (node, ch) => {
  const w = grid;
  const h = Math.max(ch, grid);
  const hh = Math.max(node.arguments.length, 1) * grid;
  const res = ['g', {w, h, class: 'gate', id: node.path},
    ['title', {}, node.width],
    ['rect', {
      class: [signed(node), widther(node.width)],
      width: grid,
      height: hh - 8,
      x: 0,
      y: -hh / 2 + 4
    }],
    ['text', {x: grid / 2, y: 5}, symbols[node.type]]
  ];
  return res;
};

const slice = (hi, lo) => '[' +
  ((hi < lo) ? '' : (hi === lo) ? lo : (hi + ':' + lo)) + ']';

const renderSlice = (node, ch) => {
  const [inp, p1, p2] = node.arguments;
  let label = node.type;
  switch (node.type) {
  case 'head': label = slice(inp.width - 1, inp.width - p1.name); break;
  case 'tail': label = slice(inp.width - p1.name - 1, 0); break;
  case 'bits': label = slice(p1.name, p2.name); break;
  case 'shl':  label = '<< ' + p1.name; break;
  case 'shr':  label = '>> ' + p1.name; break;
  case 'pad': label = (p1.name <= inp.width) ? '=' : 'ext';
  }
  const w = ceil(f.getWidth(label) + 5, grid);
  const h = Math.max(ch, grid);
  const res = ['g', {w, h},
    ['title', {}, node.type],
    ['rect', {class: 'literal', width: w - 4, height: grid - 4, x: 2, y: 2 - grid / 2}],
    ['text', {class: 'parameter', x: w / 2, y: 5}, label]
  ];
  return res;
};

const renderMux = (node, ch) => {
  const w = grid;
  const h = Math.max(ch, grid);
  // const totals = node.arguments.map(e => e.hTotal);
  // const offset0 = Math.min(totals[0], ch / 2 - grid);
  // const from = Math.min(totals[0] + totals[1] / 2, h / 2) - grid / 2;
  const res = ['g', {w, h, class: 'gate'},
    ['title', {}, node.width],
    ['path', {
      class: [signed(node), widther(node.width)],
      d: ['M', 0, -grid / 4 * 3, 'l', grid, grid / 2, 'v', grid / 4 * 5, 'l', -grid, grid / 2, 'z']
    }],
    ['path', {
      class: 'unsigned',
      d: ['M', 0, -grid, 'h', grid / 2, 'v', grid / 2]
    }],
    ['text', {x: grid / 4, y: 5}, 0],
    ['text', {x: grid / 4, y: grid + 5}, 1]
  ];
  return res;
};

const renderOther = (node, ch) => {
  const w = 2 * grid;
  const h = Math.max(ch, grid);
  return ['g', {w, h},
    ['path', {class: 'mark', d: ['M', 0, 0, 'L', grid, h / 2, 'V', h]}],
    ['text', {class: 'label', x: grid / 2, y: h / 2 + 5}, node.type],
    ['title', ['tspan', node.type]]
  ];
};

const renderCvt = (node, ch) => {
  const w = 2 * grid;
  const h = Math.max(ch, 3);
  return ['g', {w, h},
    ['line', {
      class: [
        signed(node),
        widther(node.width)
      ],
      x1: 0, y1: 0, x2: grid, y2: 0
    }],
    ['line', {
      class: [
        signed(node),
        widther(node.width)
      ],
      x1: grid, y1: 0, x2: 2 * grid, y2: 0
    }]
  ];
};

const lut = {
  input: renderInput,
  output: renderOutput,
  wire: renderWire,
  reg: renderReg, regr: renderReg, rega: renderReg,
  Int: renderLiteral,
  asSInt: renderCvt, asUInt: renderCvt, cvt: renderCvt,
  tail: renderSlice, head: renderSlice, bits: renderSlice,
  shl: renderSlice, shr: renderSlice, pad: renderSlice,
  mux: renderMux,
  parameter: renderParameter,
  other: renderOther
};

const getBody = (node, ch, reuse) =>
  (
    (shapes[node.type] && renderShape) ||
    lut[node.type] ||
    (symbols[node.type] && renderBox) ||
    lut.other
  )(node, ch, reuse);

const wire = (arg, x, y1, y2) => {
  const klass = [
    signed(arg),
    widther(arg.width)
  ];
  if (y1 == y2) {
    return ['line', {
      class: klass,
      x1: x,         y1,
      x2: x + grid,  y2
    }];
  }
  return ['path', {
    class: klass,
    d: ['M', x, y1, 'h', grid / 2, 'v', y2 - y1, 'h', grid / 2]
  }];
};

const tree = node => {

  let hTotal = node.hTotal;
  let wTotal = node.wTotal;
  let g = ['g', {}];
  let reuse = false;

  const args = (node.arguments || [])
    .filter(arg => arg.type !== 'parameter');

  if (wTotal === undefined) {
    const children = args.map(tree);

    ({wTotal, hTotal} = children.reduce((res, e) => {
      res.wTotal = Math.max(res.wTotal, e[1].w);
      res.hTotal += e[1].h;
      return res;
    }, {wTotal: 0, hTotal: 0}));

    ({g} = children.reduce((res, e, ei) => {
      res.g.push(['g', tt(wTotal - e[1].w, res.y), e]);
      res.g.push(wire(
        args[ei],
        wTotal,
        res.y + e[1].h / 2,
        hTotal / 2 + (ei - children.length / 2 + 0.5) * grid
      ));
      res.y += e[1].h;
      return res;
    }, {y: 0, g}));
    node.wTotal = wTotal;
    hTotal = node.hTotal = Math.max(hTotal, grid);
  } else {
    reuse = true;
    hTotal = node.hTotal = grid;
  }

  const body = getBody(node, hTotal, reuse);
  g.push(['g', tt(wTotal + grid, hTotal / 2), body]);
  g[1].w = wTotal + grid + body[1].w;
  g[1].h = body[1].h;
  return g;
};

const excluder = node => {
  switch(node.type) {
  case 'input':
  case 'wire':
  case 'reg':
  case 'regr':
    return false;
  // case 'output':
  //   if (node.usage > 0) { return false; }
  }
  return true;
};

const forest = circuit => {
  const res = ['g', tt(.5, .5)];
  const modBackGround = ['rect', {x: -grid / 2, y: -grid, height: 1.5 * grid}];
  let w = 256;
  let h = grid / 2;
  circuit.map(mod => {
    res.push(['g', tt(grid, h + grid),
      modBackGround,
      ['text', {class: 'modName'}, mod.name]
    ]);
    h += 2 * grid;
    mod.body.filter(excluder).map(node => {
      const e = tree(node);
      res.push(['g', tt(0, h), e]);
      h += e[1].h;
      w = Math.max(w, e[1].w);
    });
    h += grid;
  });
  res[1].w = w + grid;
  res[1].h = h + grid;
  modBackGround[1].width = w;
  return res;
};

module.exports = forest;
