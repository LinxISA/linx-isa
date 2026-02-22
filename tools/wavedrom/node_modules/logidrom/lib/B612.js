'use strict';

exports['B612'] = function() {
  const table = [
      '24',
      '30',
      '36',
      '40',
      '42',
      '48',
      '54',
      '60',
      '63',
      '66',
      '72',
      '78',
      '84',
      '90',
      '96',
      '102',
      '108',
      '114',
      '120',
      '77.890625'
    ],
    baseSize = 120,
    height = 147.34375,
    descent = 51.5703125,
    defaultWidth = 96,
    re = new RegExp('([\'\\|])|([,;])|([\\.:Ii])|([j])|([!l])|(["frt])|([\\(\\)\\-J\\[s])|([=\\]cz])|([a])|([\\$\\*/\\?FLS\\\\_`ekvxy])|([\\+CEKPTYZbdghnopqu\\}])|([0123456789<>ABDGRVX])|([&HU])|([N\\^w~])|([OQ])|([#])|([%Mm])|([W])|([@])|([\\{])');
  return function(fontSize) {
    const ratio = fontSize / baseSize;
    const getIndex = ch => {
      const m = ch.match(re);
      if (m !== null)
        for (let i = 0; i < table.length; i += 1)
          if (m[i + 1] !== undefined)
            return i;
    };
    const getWidth = str => {
      return str.split('').reduce((acc, e) => acc + (table[getIndex(e)] || defaultWidth) * ratio, 0);
    };
    return {
      getHeight: function() {
        return ratio * height;
      },
      getDescent: function() {
        return ratio * descent;
      },
      getWidth: getWidth
    };
  };
};
