'use strict';

var escapeMap = {
    '&': '&amp;',
    '"': '&quot;',
    '<': '&lt;',
    '>': '&gt;'
};

function xscape (val) {
    if (typeof val !== 'string') {
        return val;
    }
    return val.replace(
        /([&"<>])/g,
        function (_, e) {
            return escapeMap[e];
        }
    );
}

var token = /<o>|<ins>|<s>|<sub>|<sup>|<b>|<i>|<tt>|<\/o>|<\/ins>|<\/s>|<\/sub>|<\/sup>|<\/b>|<\/i>|<\/tt>/;

function update (s, cmd) {
    if (cmd.add) {
        cmd.add.split(';').forEach(function (e) {
            var arr = e.split(' ');
            s[arr[0]][arr[1]] = true;
        });
    }
    if (cmd.del) {
        cmd.del.split(';').forEach(function (e) {
            var arr = e.split(' ');
            delete s[arr[0]][arr[1]];
        });
    }
}

var trans = {
    '<o>'    : { add: 'text-decoration overline' },
    '</o>'   : { del: 'text-decoration overline' },

    '<ins>'  : { add: 'text-decoration underline' },
    '</ins>' : { del: 'text-decoration underline' },

    '<s>'    : { add: 'text-decoration line-through' },
    '</s>'   : { del: 'text-decoration line-through' },

    '<b>'    : { add: 'font-weight bold' },
    '</b>'   : { del: 'font-weight bold' },

    '<i>'    : { add: 'font-style italic' },
    '</i>'   : { del: 'font-style italic' },

    '<sub>'  : { add: 'baseline-shift sub;font-size .7em' },
    '</sub>' : { del: 'baseline-shift sub;font-size .7em' },

    '<sup>'  : { add: 'baseline-shift super;font-size .7em' },
    '</sup>' : { del: 'baseline-shift super;font-size .7em' },

    '<tt>'   : { add: 'font-family monospace' },
    '</tt>'  : { del: 'font-family monospace' }
};

function dump (s) {
    return Object.keys(s).reduce(function (pre, cur) {
        var keys = Object.keys(s[cur]);
        if (keys.length > 0) {
            pre[cur] = keys.join(' ');
        }
        return pre;
    }, {});
}

function parse (str) {
    var state, res, i, m, a;

    if (str === undefined) {
        return [];
    }

    if (typeof str === 'number') {
        return [str + ''];
    }

    if (typeof str !== 'string') {
        return [str];
    }

    res = [];

    state = {
        'text-decoration': {},
        'font-weight': {},
        'font-style': {},
        'baseline-shift': {},
        'font-size': {},
        'font-family': {}
    };

    while (true) {
        i = str.search(token);

        if (i === -1) {
            res.push(['tspan', dump(state), xscape(str)]);
            return res;
        }

        if (i > 0) {
            a = str.slice(0, i);
            res.push(['tspan', dump(state), xscape(a)]);
        }

        m = str.match(token)[0];

        update(state, trans[m]);

        str = str.slice(i + m.length);

        if (str.length === 0) {
            return res;
        }
    }
}

module.exports = parse;
/* eslint no-constant-condition: 0 */
