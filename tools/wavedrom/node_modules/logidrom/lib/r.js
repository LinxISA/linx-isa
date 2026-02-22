'use strict';

const estraverse = require('estraverse');
const renderAssign = require('./render-assign.js');

const Syntax = estraverse.Syntax;

function r (tree, options) {
  let res;
  estraverse.traverse(tree, {
    leave: function (node) {
      switch (node.type) {
      case Syntax.Identifier:
        node.aaa = node.name;
        break;
      case Syntax.BinaryExpression:
      case Syntax.LogicalExpression:
        node.aaa = [node.operator, node.left.aaa, node.right.aaa];
        break;
      case Syntax.UnaryExpression:
        node.aaa = [node.operator, node.argument.aaa];
        break;
      case Syntax.AssignmentExpression:
        node.aaa = [node.left.aaa, node.right.aaa];
        break;
      case Syntax.ExpressionStatement:
        node.aaa = node.expression.aaa;
        break;
      case Syntax.Program:
        res = { assign: node.body.map(function (e) { return e.aaa; }) };
        break;
      default:
        node.aaa = 'unknown';
      }
    }
  });
  // console.log(JSON.stringify(res));
  return renderAssign(options.index, res);
}

module.exports = r;
