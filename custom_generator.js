'use strict';

/**
 * Consideraciónes:
 * 2. No verifica que los parametros de distintas funciones se llamen diferente (No necesariamente es un
 *    problema pero hay que verificar conflictos con tipos por variables sobre escritas).
 * 3. Ciclos FOR no verifican el tipo de la variable a iterar (pero no hay problema si se usa la variable
 *    que se crea por defecto)
 * 4. Una vez declarado un parametro no se puede cambiar su tipo o nombre *Funcionamiento intencionado*
 *    (Hay que eliminarlo y crear uno nuevo)
 * 5. Ignorar condicional ifelse
 * */

// CUSTOM GENERATOR
const customGenerator = new Blockly.Generator('DALE++');

customGenerator.addReservedWords(
  'program,var,int,float,char,fun,void,return,main,if,else,read,write,for,to,while,' +
  Object.getOwnPropertyNames(Blockly.utils.global).join(',')
);

customGenerator.ORDER_ATOMIC = 0;           // 0 "" ...
customGenerator.ORDER_MEMBER = 1;         // . []
customGenerator.ORDER_FUNCTION_CALL = 2;    // ()
customGenerator.ORDER_VOID = 3;           // void
customGenerator.ORDER_MULTIPLICATION = 4.1; // *
customGenerator.ORDER_DIVISION = 4.2;       // /
customGenerator.ORDER_SUBTRACTION = 5.1;    // -
customGenerator.ORDER_ADDITION = 5.2;       // +
customGenerator.ORDER_RELATIONAL = 6;       // < <= > >=
customGenerator.ORDER_EQUALITY = 7;         // == !=
customGenerator.ORDER_LOGICAL_AND = 8;     // &&
customGenerator.ORDER_LOGICAL_OR = 9;      // ||
customGenerator.ORDER_ASSIGNMENT = 10;      // =
customGenerator.ORDER_COMMA = 11;           // ,
customGenerator.ORDER_NONE = 99;            // (...)

customGenerator.ORDER_OVERRIDES = [
  // (foo()).bar -> foo().bar
  // (foo())[0] -> foo()[0]
  [customGenerator.ORDER_FUNCTION_CALL, customGenerator.ORDER_MEMBER],
  // (foo())() -> foo()()
  [customGenerator.ORDER_FUNCTION_CALL, customGenerator.ORDER_FUNCTION_CALL],
  // (foo.bar).baz -> foo.bar.baz
  // (foo.bar)[0] -> foo.bar[0]
  // (foo[0]).bar -> foo[0].bar
  // (foo[0])[1] -> foo[0][1]
  [customGenerator.ORDER_MEMBER, customGenerator.ORDER_MEMBER],
  // (foo.bar)() -> foo.bar()
  // (foo[0])() -> foo[0]()
  [customGenerator.ORDER_MEMBER, customGenerator.ORDER_FUNCTION_CALL],
  // a * (b * c) -> a * b * c
  [customGenerator.ORDER_MULTIPLICATION, customGenerator.ORDER_MULTIPLICATION],
  // a + (b + c) -> a + b + c
  [customGenerator.ORDER_ADDITION, customGenerator.ORDER_ADDITION],
  // a && (b && c) -> a && b && c
  [customGenerator.ORDER_LOGICAL_AND, customGenerator.ORDER_LOGICAL_AND],
  // a || (b || c) -> a || b || c
  [customGenerator.ORDER_LOGICAL_OR, customGenerator.ORDER_LOGICAL_OR]
];

customGenerator.init = (workspace) => {
  let i;
// Create a dictionary of definitions to be printed before the code.
  customGenerator.definitions_ = Object.create(null);
  // Create a dictionary mapping desired function names in definitions_
  // to actual function names (to avoid collisions with user functions).
  customGenerator.functionNames_ = Object.create(null);

  if (!customGenerator.variableDB_) {
    customGenerator.variableDB_ =
      new Blockly.Names(customGenerator.RESERVED_WORDS_);
  } else {
    customGenerator.variableDB_.reset();
  }

  customGenerator.variableDB_.setVariableMap(workspace.getVariableMap());

  let defvars = [];
  // Add developer variables (not created or named by the user).
  let devVarList = Blockly.Variables.allDeveloperVariables(workspace);
  for (i = 0; i < devVarList.length; i++) {
    defvars.push(customGenerator.variableDB_.getName(devVarList[i],
      Blockly.Names.DEVELOPER_VARIABLE_TYPE));
  }

  // Add user variables, but only ones that are being used.
  let variables = Blockly.Variables.allUsedVarModels(workspace);
  for (i = 0; i < variables.length; i++) {
    defvars.push(customGenerator.variableDB_.getName(variables[i].getId(),
      Blockly.VARIABLE_CATEGORY_NAME));
  }

  // Declare all of the variables.
  if (defvars.length) {
    customGenerator.definitions_['variables'] =
      'var ' + defvars.join(', ') + ';';
  }
};

customGenerator.finish = (code) => {
  // Clean up temporary data.
  delete customGenerator.definitions_;
  delete customGenerator.functionNames_;
  customGenerator.variableDB_.reset();
  return code;
};

// Remove blocks that aren't connected to anything *optional
customGenerator.scrubNakedValue = function (line) {
  return '';
};

customGenerator.quote_ = (string) => {
  string = string.replace(/\\/g, '\\\\')
    .replace(/\n/g, '\\\n')
    .replace(/'/g, '\\\'');
  if (string.length <= 1) {
    return '\'' + string + '\'';
  }
  return '\"' + string + '\"';
};

customGenerator.getAdjusted = (block, atId, opt_delta, opt_negate, opt_order) => {
  let innerOrder;
  let delta = opt_delta || 0;
  let order = opt_order || customGenerator.ORDER_NONE;
  if (block.workspace.options.oneBasedIndex) {
    delta--;
  }
  const defaultAtIndex = block.workspace.options.oneBasedIndex ? '1' : '0';
  let at;
  if (delta > 0) {
    at = customGenerator.valueToCode(block, atId,
      customGenerator.ORDER_ADDITION) || defaultAtIndex;
  } else if (delta < 0) {
    at = customGenerator.valueToCode(block, atId,
      customGenerator.ORDER_SUBTRACTION) || defaultAtIndex;
  } else {
    at = customGenerator.valueToCode(block, atId, order) ||
      defaultAtIndex;
  }

  if (Blockly.isNumber(at)) {
    // If the index is a naked number, adjust it right now.
    at = Number(at) + delta;
    if (opt_negate) {
      at = -at;
    }
  } else {
    // If the index is dynamic, adjust it in code.
    if (delta > 0) {
      at = at + ' + ' + delta;
      innerOrder = customGenerator.ORDER_ADDITION;
    } else if (delta < 0) {
      at = at + ' - ' + -delta;
      innerOrder = customGenerator.ORDER_SUBTRACTION;
    }
    innerOrder = Math.floor(innerOrder);
    order = Math.floor(order);
    if (innerOrder && order >= innerOrder) {
      at = '(' + at + ')';
    }
  }
  return at;
};

customGenerator.scrub_ = (block, code, opt_thisOnly) => {
  const nextBlock =
    block.nextConnection && block.nextConnection.targetBlock();
  const nextCode =
    opt_thisOnly ? '' : customGenerator.blockToCode(nextBlock);
  return code + nextCode;
};

// TEXT
customGenerator['text'] = (block) => {
  const string = customGenerator.quote_(block.getFieldValue('TEXT'));
  return [string, customGenerator.ORDER_ATOMIC];
};

// ARITHMETIC
customGenerator['math_number'] = (block) => {
  // Numeric value.
  let code = Number(block.getFieldValue('NUM'));
  return [code, customGenerator.ORDER_ATOMIC];
};

customGenerator['arithmetic_operation'] = (block) => {
  // Basic arithmetic operators, and power.
  const OPERATORS = {
    'ADD': [' + ', customGenerator.ORDER_ADDITION],
    'MINUS': [' - ', customGenerator.ORDER_SUBTRACTION],
    'MULTIPLY': [' * ', customGenerator.ORDER_MULTIPLICATION],
    'DIVIDE': [' / ', customGenerator.ORDER_DIVISION]
  };
  const tuple = OPERATORS[block.getFieldValue('OPERATOR')];
  const operator = tuple[0];
  const order = tuple[1];
  const argument0 = customGenerator.valueToCode(block, 'LEFT_OPERAND', order);
  const argument1 = customGenerator.valueToCode(block, 'RIGHT_OPERAND', order);
  let code = argument0 + operator + argument1;
  return [code, order];
};

// PROGRAM
customGenerator['program'] = (block) => {
  const id = block.getFieldValue('ID');
  return 'program ' + id + '\n';
};

// MAIN
customGenerator['main'] = (block) => {
  let branch = customGenerator.statementToCode(block, 'BRANCH');
  let code;
  code = 'main () {\n' + branch + '}';
  return code;
};

// FUNCTIONS
customGenerator['procedures_defreturn'] = (block) => {
  const funName = customGenerator.variableDB_.getName(block.getFieldValue('NAME'), Blockly.PROCEDURE_CATEGORY_NAME);
  const type = block.getFieldValue('RETURN_TYPE')
  const branch = customGenerator.statementToCode(block, 'STACK');
  let returnValue = customGenerator.valueToCode(block, 'RETURN',
    customGenerator.ORDER_NONE) || '';
  if (returnValue) {
    returnValue = customGenerator.INDENT + 'return (' + returnValue + ')\n';
  }

  let code = 'fun ' + funName + '(';
  const variables = block.getVarModels();
  for (let i = 0; i < variables.length; i++) {
    code += customGenerator.variableDB_.getName(variables[i].name, Blockly.VARIABLE_CATEGORY_NAME)
      + ': ' + variables[i].type + ', ';
  }
  if (variables.length > 0)
    code = code.substring(0, code.length - 2);
  code += '): ' + type + ' {\n' + branch + returnValue + '}\n';
  return code;
};

// Defining a procedure without a return value uses the same generator as
// a procedure with a return value.
customGenerator['procedures_defnoreturn'] = (block) => {
  const funName = customGenerator.variableDB_.getName(
    block.getFieldValue('NAME'), Blockly.PROCEDURE_CATEGORY_NAME);
  const branch = customGenerator.statementToCode(block, 'STACK');
  let returnValue = customGenerator.valueToCode(block, 'RETURN',
    customGenerator.ORDER_NONE) || '';
  if (returnValue) {
    returnValue = customGenerator.INDENT + 'return ' + returnValue + '\n';
  }

  let code = 'fun ' + funName + '(';
  const variables = block.getVarModels();
  for (let i = 0; i < variables.length; i++) {
    code += customGenerator.variableDB_.getName(variables[i].name, Blockly.VARIABLE_CATEGORY_NAME)
      + ': ' + variables[i].type + ', ';
  }
  if (variables.length > 0)
    code = code.substring(0, code.length - 2);
  code += '): void {\n' + branch + returnValue + '}\n';
  return code;
};

customGenerator['procedures_callreturn'] = (block) => {
  // Call a procedure with a return value.
  const funcName = customGenerator.variableDB_.getName(
    block.getFieldValue('NAME'), Blockly.PROCEDURE_CATEGORY_NAME);
  const args = [];
  const variables = block.getVars();
  for (let i = 0; i < variables.length; i++) {
    args[i] = customGenerator.valueToCode(block, 'ARG' + i,
      customGenerator.ORDER_COMMA);
  }
  const code = funcName + '(' + args.join(', ') + ')';
  return [code, customGenerator.ORDER_FUNCTION_CALL];
};

customGenerator['procedures_callnoreturn'] = (block) => {
  // Call a procedure with no return value.
  // Generated code is for a function call as a statement is the same as a
  // function call as a value, with the addition of line ending.
  const tuple = customGenerator['procedures_callreturn'](block);
  return tuple[0] + '\n';
};

Blockly.Blocks['procedures_ifreturn'] = false;

// LOGIC
customGenerator['controls_if'] = (block) => {
  // If/elseif/else condition.
  let n = 0;
  let code = '', branchCode, conditionCode;
  if (customGenerator.STATEMENT_PREFIX) {
    // Automatic prefix insertion is switched off for this block.  Add manually.
    code += customGenerator.injectId(customGenerator.STATEMENT_PREFIX, block);
  }
  do {
    conditionCode = customGenerator.valueToCode(block, 'IF' + n,
      customGenerator.ORDER_NONE);
    branchCode = customGenerator.statementToCode(block, 'DO' + n);
    if (customGenerator.STATEMENT_SUFFIX) {
      branchCode = customGenerator.prefixLines(
        customGenerator.injectId(customGenerator.STATEMENT_SUFFIX, block), customGenerator.INDENT) + branchCode;
    }
    code += (n > 0 ? ' else ' : '') +
      'if (' + conditionCode + ') {\n' + branchCode + '}';
    ++n;
  } while (block.getInput('IF' + n));

  if (block.getInput('ELSE') || customGenerator.STATEMENT_SUFFIX) {
    branchCode = customGenerator.statementToCode(block, 'ELSE');
    if (customGenerator.STATEMENT_SUFFIX) {
      branchCode = customGenerator.prefixLines(
        customGenerator.injectId(customGenerator.STATEMENT_SUFFIX,
          block), customGenerator.INDENT) + branchCode;
    }
    code += ' else {\n' + branchCode + '}';
  }
  return code + '\n';
};

customGenerator['controls_ifelse'] = customGenerator['controls_if'];

customGenerator['logic_compare'] = (block) => {
  // Comparison operator.
  const OPERATORS = {
    'EQ': '==',
    'NEQ': '!=',
    'LT': '<',
    'LTE': '<=',
    'GT': '>',
    'GTE': '>='
  };
  const operator = OPERATORS[block.getFieldValue('OP')];
  const order = (operator === '==' || operator === '!=') ?
    customGenerator.ORDER_EQUALITY : customGenerator.ORDER_RELATIONAL;
  const argument0 = customGenerator.valueToCode(block, 'A', order);
  const argument1 = customGenerator.valueToCode(block, 'B', order);
  const code = argument0 + ' ' + operator + ' ' + argument1;
  return [code, order];
};

customGenerator['logic_operation'] = (block) => {
  // Operations 'and', 'or'.
  const operator = (block.getFieldValue('OP') === 'AND') ? '&&' : '||';
  const order = (operator === '&&') ? customGenerator.ORDER_LOGICAL_AND :
    customGenerator.ORDER_LOGICAL_OR;
  let argument0 = customGenerator.valueToCode(block, 'A', order);
  let argument1 = customGenerator.valueToCode(block, 'B', order);
  if (!argument0 && !argument1) {
    argument0 = '';
    argument1 = '';
  } else {
    // Single missing arguments have no effect on the return value.
    const defaultArgument = (operator === '&&') ? 'true' : 'false';
    if (!argument0) {
      argument0 = defaultArgument;
    }
    if (!argument1) {
      argument1 = defaultArgument;
    }
  }
  const code = argument0 + ' ' + operator + ' ' + argument1;
  return [code, order];
};

// LOOPS
customGenerator['for_loop'] = (block) => {
  // For loop.
  const var_name = customGenerator.variableDB_.getName(
    block.getFieldValue('VAR'), Blockly.VARIABLE_CATEGORY_NAME);
  const value_from = customGenerator.valueToCode(block, 'FROM',
    customGenerator.ORDER_ASSIGNMENT);
  const value_to = customGenerator.valueToCode(block, 'TO',
    customGenerator.ORDER_ASSIGNMENT);
  let branch = customGenerator.statementToCode(block, 'DO');
  let code;
  code = 'for ' + var_name + ' = ' + value_from + ' to ' + value_to + ' {\n' + branch + '}\n';
  return code;
};

customGenerator['while_loop'] = (block) => {
  // While loop.
  const bool_expression = customGenerator.valueToCode(block, 'BOOL',
    customGenerator.ORDER_ASSIGNMENT);
  let branch = customGenerator.statementToCode(block, 'DO');
  let code;
  code = 'while (' + bool_expression + ') {\n' + branch + '}\n';
  return code;
};

// WRITE
customGenerator['write'] = (block) => {
  const value = customGenerator.valueToCode(block, 'VALUE', customGenerator.ORDER_NONE);
  return 'write(' + value + ')\n';
}

// WRITE
customGenerator['read'] = (block) => {
  const var_name = customGenerator.variableDB_.getName(
    block.getFieldValue('VAR'), Blockly.VARIABLE_CATEGORY_NAME);
  return 'read(' + var_name + ')\n';
}

// VARIABLES
customGenerator['variable_declaration'] = (block) => {
  const name = customGenerator.variableDB_.getName(block.getFieldValue('VAR'), Blockly.VARIABLE_CATEGORY_NAME);
  let code = 'var ' + name;
  const varType = block.getVarModels()[0].type;
  const dim1 = block.getFieldValue('DIM1');
  if (varType.indexOf('-') !== -1) {
    code += '[' + dim1 + ']';
  }
  const dim2 = block.getFieldValue('DIM2');
  if (varType.indexOf('matrix') !== -1) {
    code += '[' + dim2 + ']';
  }
  const type = block.getFieldValue('TYPE');
  code += ': ' + type + '\n';
  return code;
}

customGenerator['variables_set'] = (block) => {
  const name = customGenerator.variableDB_.getName(block.getFieldValue('VAR'), Blockly.VARIABLE_CATEGORY_NAME);
  let code = name;
  const type = block.getVarModels()[0].type;
  const dim1 = customGenerator.valueToCode(block, 'DIM1', customGenerator.ORDER_NONE);
  if (type.indexOf('-') !== -1) {
    code += '[' + dim1 + ']';
  }
  const dim2 = customGenerator.valueToCode(block, 'DIM2', customGenerator.ORDER_NONE);
  if (type.indexOf('matrix') !== -1) {
    code += '[' + dim2 + ']';
  }
  const value = customGenerator.valueToCode(block, 'VALUE', customGenerator.ORDER_NONE);
  code += ' = ' + value + '\n';
  return code;
}

customGenerator['variables_get'] = (block) => {
  const name = customGenerator.variableDB_.getName(block.getFieldValue('VAR'), Blockly.VARIABLE_CATEGORY_NAME);
  let code = name;
  const type = block.getVarModels()[0].type;
  const dim1 = customGenerator.valueToCode(block, 'DIM1', customGenerator.ORDER_NONE);
  if (type.indexOf('-') !== -1) {
    code += '[' + dim1 + ']';
  }
  const dim2 = customGenerator.valueToCode(block, 'DIM2', customGenerator.ORDER_NONE);
  if (type.indexOf('matrix') !== -1) {
    code += '[' + dim2 + ']';
  }
  return [code, customGenerator.ORDER_ATOMIC];
};

customGenerator['variables_get_dynamic'] = customGenerator['variables_get'];
customGenerator['variables_set_dynamic'] = customGenerator['variables_set'];

// CUSTOM CATEGORY
Blockly.Blocks['math_change'] = false

Blockly.VariablesDynamic.flyoutCategoryBlocks = (workspace) => {
  let block;
  const variableModelList = workspace.getAllVariables();

  const xmlList = [];
  if (variableModelList.length > 0) {
    // New variables are added to the end of the variableModelList.
    const mostRecentVariable = variableModelList[variableModelList.length - 1];
    if (Blockly.Blocks['variables_set_dynamic']) {
      block = Blockly.utils.xml.createElement('block');
      block.setAttribute('type', 'variables_set_dynamic');
      block.setAttribute('gap', 24);
      block.appendChild(
        Blockly.Variables.generateVariableFieldDom(mostRecentVariable));
      xmlList.push(block);
    }

    if (Blockly.Blocks['variables_get_dynamic']) {
      block = Blockly.utils.xml.createElement('block');
      block.setAttribute('type', 'variables_get_dynamic');
      block.setAttribute('gap', 24);
      block.appendChild(
        Blockly.Variables.generateVariableFieldDom(mostRecentVariable));
      xmlList.push(block);
    }

    if (Blockly.Blocks['variable_declaration']) {
      variableModelList.sort(Blockly.VariableModel.compareByName);
      for (let i = 0, variable; (variable = variableModelList[i]); i++) {
        let uses = workspace.getVariableUsesById(variable.getId())
        let needsDeclaration = true;
        for (let i = 0, block; (block = uses[i]); i++) {
          if (block.type === 'procedures_defnoreturn' || block.type === 'procedures_defreturn') {
            needsDeclaration = false;
            break;
          }
        }
        if (needsDeclaration && variable.name !== "default") {
          block = Blockly.utils.xml.createElement('block');
          block.setAttribute('type', 'variable_declaration');
          block.setAttribute('gap', 8);
          block.appendChild(
            Blockly.Variables.generateVariableFieldDom(variable));
          xmlList.push(block);
        }
      }
    }
  }
  return xmlList;
};

const createFlyout = (workspace) => {
  let xmlList = [];
  // Add your button and give it a callback name.
  const button = document.createElement('button');
  button.setAttribute('text', 'Create Variable');
  button.setAttribute('callbackKey', 'callbackName');

  xmlList.push(button);

  // This gets all the variables that the user creates and adds them to the
  // flyout.
  const blockList = Blockly.VariablesDynamic.flyoutCategoryBlocks(workspace);
  xmlList = xmlList.concat(blockList);

  return xmlList;
};
