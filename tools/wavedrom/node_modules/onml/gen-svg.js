'use strict';

const w3 = {
  svg: 'http://www.w3.org/2000/svg',
  xlink: 'http://www.w3.org/1999/xlink',
  xmlns: 'http://www.w3.org/XML/1998/namespace'
};

module.exports = (w, h) => ['svg', {
  xmlns: w3.svg, 'xmlns:xlink': w3.xlink,
  width: w, height: h,
  viewBox: '0 0 ' + w + ' ' + h
}];
