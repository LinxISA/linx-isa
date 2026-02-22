# &lt;tspan&gt;

[![NPM version](https://img.shields.io/npm/v/tspan.svg)](https://www.npmjs.org/package/tspan)
[![Build Status](https://travis-ci.org/drom/tspan.svg)](https://travis-ci.org/drom/tspan)
[![Coverage Status](https://coveralls.io/repos/github/drom/tspan/badge.svg?branch=master)](https://coveralls.io/github/drom/tspan?branch=master)

**tspan** is an JavaScript library designed for a simple way of adding some formated text into SVG documents. It takes text string with some XML style tags and produces an array of `<tspan>` objects in [JsonML](http://www.jsonml.org) format.

### Supported tags:

|format|render|SVG style|
|------|------|---------|
|`<o>overline</o>`|<o>overline</o>|{'text-decoration': 'overline'}
|`<ins>underline</ins>`|<ins>underline</ins>|{'text-decoration': 'underline'}
|`<sub>subscript</sub>`|<sub>subscript</sub>|{'baseline-shift': 'sub'}
|`<sup>superscript</sup>`|<sup>superscript</sup>|{'baseline-shift': 'super'}
|`<b>bold</b>`|<b>bold</b>|{'font-weight': 'bold'}
|`<i>italic</i>`|<i>italic</i>|{'font-style': 'italic'}
|`<s>strikethrough</s>`|<s>strikethrough</s>|{'text-decoration': 'line-through'}
|`<tt>code</tt>`|<tt>code</tt>|{'font-family': 'monospace'}

#### Resulted SVG

![exmaple](https://rawgit.com/drom/tspan/master/test/all.svg)

## Use
### Node.js

```
npm i tspan --save
```

```js
var tspan = require('tspan');

var source = 'a <o>long</o> <i>and <b>winding</i> <sub>road</sub>';
var result = tspan.parse(source);

console.log(result);
// -->
[
    ['tspan', {}, 'a '],
    ['tspan', {'text-decoration': 'overline'}, 'long'],
    ['tspan', {}, ' '],
    ['tspan', {'font-style': 'italic'}, 'and '],
    ['tspan', {'font-style': 'italic', 'font-weight': 'bold'}, 'winding'],
    ['tspan', {'font-weight': 'bold'}, ' '],
    ['tspan', {'baseline-shift': 'sub', 'font-size': '.7em', 'font-weight': 'bold'}, 'road']
]
```
tspan array then can be unshifted with a `text` tag, inserted into bigger SVG structure and with a little help of [onml](https://www.npmjs.com/package/onml) package converted into XML form.

```js
result.unshift('text', {x: 20, y: 20, 'font-size': 16});
var svg = ['svg', {
    viewBox: '0 0 400 100',
    width: 400, height: 100,
    xmlns: 'http://www.w3.org/2000/svg'
}, result];

var onml = require('onml');

console.log(onml.stringify(svg)));
// -->
<svg viewBox="0 0 400 100" width="400" height="100" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="20" font-size="16">
    <tspan>a </tspan>
    <tspan text-decoration="overline">long</tspan>
    <tspan></tspan>
    <tspan font-style="italic">and </tspan>
    <tspan font-style="italic" font-weight="bold">winding</tspan>
    <tspan font-weight="bold"></tspan>
    <tspan baseline-shift="sub" font-size=".7em" font-weight="bold">road</tspan>
  </text>
</svg>
```

that will look like:

![exmaple](https://rawgit.com/drom/tspan/master/test/alawr.svg)

### Browser

*Browserify!*

## Testing
`npm test`

## License
MIT [LICENSE](https://github.com/drom/tspan/blob/master/LICENSE).
