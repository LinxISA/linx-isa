# ONML

[![NPM version](https://img.shields.io/npm/v/onml.svg)](https://www.npmjs.org/package/onml)
[![Actions Status](https://github.com/drom/onml/workflows/Tests/badge.svg)](https://github.com/drom/onml/actions)

[jsonml.org](http://www.jsonml.org/) compatible tool set.

## Use
### Node.js

```
npm i onml --save
```

```js
var onml = require('onml');
```

## API
### onml.parse() --- onml.p()
The `onml.parse()` method parses a XML/HTML/SVG string and returns a JavaScript value.

```js
var obj = onml.parse('<text a="5">so me</text>');
console.log(obj);
-->
["text", {a: "5"}, "so me"]
```

### onml.stringify() --- onml.s()
The `onml.stringify(array, [indentation])` method converts a JavaScript value to a XML/HTML/SVG string.

```js
var str = onml.stringify(['text', {a: 55}, 'so me'], 2);
console.log(str);
-->
<text a="55">
  so me
</text>
```

### onml.traverse() --- onml.t()
JSONML object traversal tool. See [test/traverse.js](test/traverse.js) for more details.

```js
onml.traverse(obj, {
    enter: function (node, parent) {
        ...
    },
    leave: function (node, parent) {
        ...
    }
});
```
Inside `enter` and `leave` functions:

`node` and `parent` objects have the following attributes:
  * `.name` -- tag name
  * `.attr` -- attributes object
  * `.full` -- full node array

`this` will hold additional methods:
  * `this.name(string)` -- to change the node tag
  * `this.skip()` -- to skip subtree based on the current node
  * `this.remove()` -- to remove current node
  * `this.replace(array)` -- to replace current node

```js
// count divs on enter
var count = 0;
onml.traverse(
    ['b',
        ['div', {a: true},
            ['span',
                'div',
                ['div',
                    ['div', {},
                        ['div', {a: true}]
                    ]
                ],
                ['div', {},
                    ['div']
                ]
            ]
        ]
    ],
    {
        enter: function (node) {
            if (node.name === 'div') {
                count++;
            }
        }
    }
);
console.log(count);
-->
6
```

## Testing
`npm test`

## License
MIT [LICENSE](https://github.com/drom/onml/blob/master/LICENSE).
