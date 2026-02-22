'use strict';

function render(tree, state) {
  // var y, i, ilen;

  state.xmax = Math.max(state.xmax, state.x);

  const y = state.y;
  const ilen = tree.length;

  for (let i = 1; i < ilen; i++) {
    const branch = tree[i];
    if (Array.isArray(branch)) {
      state = render(branch, {
        x: (state.x + 1),
        y: state.y,
        xmax: state.xmax
      });
    } else {
      tree[i] = {
        name: branch,
        x: (state.x + 1),
        y: state.y
      };
      state.y += 2;
    }
  }

  tree[0] = {
    name: tree[0],
    x: state.x,
    y: Math.round((y + (state.y - 2)) / 2)
  };

  state.x--;
  return state;
}

module.exports = render;
