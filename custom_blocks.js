Blockly.Msg["PROCEDURES_DEFNORETURN_TITLE"] = "fun";
Blockly.Msg["PROCEDURES_DEFRETURN_TITLE"] = Blockly.Msg["PROCEDURES_DEFNORETURN_TITLE"];
Blockly.Msg["PROCEDURES_DEFNORETURN_PROCEDURE"] = "my_fun";
Blockly.Msg["PROCEDURES_DEFRETURN_PROCEDURE"] = Blockly.Msg["PROCEDURES_DEFNORETURN_PROCEDURE"];
Blockly.Msg["PROCEDURES_BEFORE_PARAMS"] = "";
Blockly.Msg["PROCEDURES_CALL_BEFORE_PARAMS"] = "args:";
Blockly.Msg["VARIABLES_SET"] = "%1 = %2";
Blockly.Msg["VARIABLE_DECLARATION"] = "var %1 : %2";

// CUSTOM BLOCKS
Blockly.defineBlocksWithJsonArray([
  // ARITHMETIC
  {
    "type": "arithmetic_operation",
    "message0": "%1 %2 %3",
    "args0": [
      {
        "type": "input_value",
        "name": "LEFT_OPERAND",
        "check": ["int", "float"]
      },
      {
        "type": "field_dropdown",
        "name": "OPERATOR",
        "options": [
          [
            "+",
            "ADD"
          ],
          [
            "-",
            "MINUS"
          ],
          [
            "*",
            "MULTIPLY"
          ],
          [
            "/",
            "DIVIDE"
          ]
        ]
      },
      {
        "type": "input_value",
        "name": "RIGHT_OPERAND",
        "check": ["int", "float"],
        "align": "RIGHT"
      }
    ],
    "inputsInline": true,
    "output": ["int", "float"],
    "colour": 230,
    "tooltip": "Operación Aritmética",
    "helpUrl": ""
  },
  // LOOPS
  // FOR
  {
    "type": "for_loop",
    "message0": "for %1 = %2 to %3",
    "args0": [
      {
        "type": "field_variable",
        "name": "VAR",
        "variable": null
      },
      {
        "type": "input_value",
        "name": "FROM",
        "check": "int",
        "align": "RIGHT"
      },
      {
        "type": "input_value",
        "name": "TO",
        "check": "int",
        "align": "RIGHT"
      }
    ],
    "message1": "do %1",
    "args1": [{
      "type": "input_statement",
      "name": "DO"
    }],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "style": "loop_blocks",
    "helpUrl": "",
    "extensions": [
      "contextMenu_newGetVariableBlock"
    ]
  },
  // WHILE
  {
    "type": "while_loop",
    "message0": "while %1",
    "args0": [
      {
        "type": "input_value",
        "name": "BOOL",
        "check": "Boolean"
      }
    ],
    "message1": "do %1",
    "args1": [{
      "type": "input_statement",
      "name": "DO"
    }],
    "previousStatement": null,
    "nextStatement": null,
    "style": "loop_blocks",
    "helpUrl": ""
  },
  // MAIN
  {
    "type": "main",
    "message0": "main %1",
    "args0": [
      {
        "type": "input_statement",
        "name": "BRANCH"
      }
    ],
    "colour": 290,
    "tooltip": "Main",
    "helpUrl": ""
  },
  // PROGRAM
  {
    "type": "program",
    "message0": "program id = %1",
    "args0": [
      {
        "type": "field_input",
        "name": "ID",
        "text": "my_program"
      }
    ],
    "inputsInline": false,
    "colour": 260,
    "tooltip": "",
    "helpUrl": ""
  },
  //WRITE
  {
    "type": "write",
    "message0": "Write %1",
    "args0": [
      {
        "type": "input_value",
        "name": "VALUE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 260,
    "tooltip": "",
    "helpUrl": ""
  },
  // READ
  {
    "type": "read",
    "message0": "read %1",
    "args0": [
      {
        "type": "field_variable",
        "name": "VAR",
        "variable": "default"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": 230,
    "tooltip": "",
    "helpUrl": ""
  }
]);

// TEXT
Blockly.Blocks['text'].validator = function (newValue) {
  let length = newValue.toString().length
  if (length > 1) {
    this.getSourceBlock().setOutput(true, 'String')
    return newValue;
  } else if (length === 1) {
    this.getSourceBlock().setOutput(true, 'char')
    return newValue;
  }
  return null;
};

Blockly.Blocks['text'].init = function () {
  this.appendDummyInput()
    .appendField(new Blockly.FieldTextInput('', this.validator), 'TEXT');
  this.setStyle('text_blocks');
  this.setOutput(true, ["String", "char"]);
  Blockly.Extensions.apply('text_quotes', this, false);
};

// MATH_NUMBER
Blockly.Blocks['math_number'].validator = function (newValue) {
  let floatRegex = /\d+\.\d+$/
  let intRegex = /\d+$/
  if (floatRegex.exec(newValue.toString()) != null) {
    this.getSourceBlock().setOutput(true, 'float')
    return newValue;
  } else if (intRegex.exec(newValue.toString()) != null) {
    this.getSourceBlock().setOutput(true, 'int')
    return newValue;
  }
  return null;
};

Blockly.Blocks['math_number'].init = function () {
  this.appendDummyInput()
    .appendField(new Blockly.FieldTextInput(0, this.validator), 'NUM');
  this.setStyle('math_blocks');
  this.setOutput(true, "int");
};

// FUNCTIONS
// VOID
Blockly.Blocks['procedures_defnoreturn'].init = function () {
  const nameField = new Blockly.FieldTextInput('', Blockly.Procedures.rename);
  nameField.setSpellcheck(false);
  this.appendDummyInput()
    .appendField(Blockly.Msg['PROCEDURES_DEFNORETURN_TITLE'])
    .appendField(nameField, 'NAME')
    .appendField('(')
    .appendField('', 'PARAMS')
    .appendField(')  :  void');
  this.setMutator(new Blockly.Mutator(['procedures_mutatorarg']));
  if ((this.workspace.options.comments ||
    (this.workspace.options.parentWorkspace &&
      this.workspace.options.parentWorkspace.options.comments)) &&
    Blockly.Msg['PROCEDURES_DEFNORETURN_COMMENT']) {
    this.setCommentText(Blockly.Msg['PROCEDURES_DEFNORETURN_COMMENT']);
  }
  this.setStyle('procedure_blocks');
  this.setTooltip(Blockly.Msg['PROCEDURES_DEFNORETURN_TOOLTIP']);
  this.setHelpUrl(Blockly.Msg['PROCEDURES_DEFNORETURN_HELPURL']);
  this.arguments_ = [];
  this.argumentVarModels_ = [];
  this.setStatements_(true);
  this.statementConnection_ = null;
};

Blockly.Blocks['procedures_defnoreturn'].updateParams_ = function () {
  let paramString = '';
  if (this.argumentVarModels_.length) {
    paramString = Blockly.Msg['PROCEDURES_BEFORE_PARAMS']
    for (let i = 0; i < this.argumentVarModels_.length; i++) {
      paramString += (this.argumentVarModels_[i].name + ':' + this.argumentVarModels_[i].type + ', ')
    }
    paramString = paramString.substring(0, paramString.length - 2);
  }
  Blockly.Events.disable();
  try {
    this.setFieldValue(paramString, 'PARAMS');
  } finally {
    Blockly.Events.enable();
  }
}

Blockly.Blocks['procedures_defnoreturn'].compose = function (containerBlock) {
  // Parameter list.
  this.arguments_ = [];
  this.paramIds_ = [];
  this.argumentVarModels_ = [];
  let paramBlock = containerBlock.getInputTargetBlock('STACK');
  while (paramBlock) {
    const varName = paramBlock.getFieldValue('NAME');
    const varType = paramBlock.getFieldValue('TYPE');
    this.arguments_.push(varName);
    const variable = this.workspace.getVariable(varName, varType);
    if (variable != null) {
      this.argumentVarModels_.push(variable);
    } else {
      console.log('Failed to create a variable with name ' + varName + ', ignoring.');
    }

    this.paramIds_.push(paramBlock.id);
    paramBlock = paramBlock.nextConnection &&
      paramBlock.nextConnection.targetBlock();
  }
  this.updateParams_();
  Blockly.Procedures.mutateCallers(this);

  // Show/hide the statement input.
  let hasStatements = containerBlock.getFieldValue('STATEMENTS');
  if (hasStatements !== null) {
    hasStatements = hasStatements === 'TRUE';
    if (this.hasStatements_ !== hasStatements) {
      if (hasStatements) {
        this.setStatements_(true);
        // Restore the stack, if one was saved.
        Blockly.Mutator.reconnect(this.statementConnection_, this, 'STACK');
        this.statementConnection_ = null;
      } else {
        // Save the stack, then disconnect it.
        const stackConnection = this.getInput('STACK').connection;
        this.statementConnection_ = stackConnection.targetConnection;
        if (this.statementConnection_) {
          const stackBlock = stackConnection.targetBlock();
          stackBlock.unplug();
          stackBlock.bumpNeighbours();
        }
        this.setStatements_(false);
      }
    }
  }
}

// WITH RETURN
Blockly.Blocks['procedures_defreturn'].validate = function (newValue) {
  this.getSourceBlock().updateConnections(newValue);
  return newValue;
};

Blockly.Blocks['procedures_defreturn'].updateConnections = function (newValue) {
  this.removeInput('RETURN', true);
  if (newValue === 'int') {
    this.appendValueInput('RETURN')
      .setCheck(['int'])
      .setAlign(Blockly.ALIGN_RIGHT)
      .appendField(Blockly.Msg['PROCEDURES_DEFRETURN_RETURN']);
  } else if (newValue === 'float') {
    this.appendValueInput('RETURN')
      .setCheck(['float'])
      .setAlign(Blockly.ALIGN_RIGHT)
      .appendField(Blockly.Msg['PROCEDURES_DEFRETURN_RETURN']);
  } else if (newValue === 'char') {
    this.appendValueInput('RETURN')
      .setCheck(['char'])
      .setAlign(Blockly.ALIGN_RIGHT)
      .appendField(Blockly.Msg['PROCEDURES_DEFRETURN_RETURN']);
  }
};

Blockly.Blocks['procedures_defreturn'].init = function () {
  const nameField = new Blockly.FieldTextInput('', Blockly.Procedures.rename);
  nameField.setSpellcheck(false);
  this.appendDummyInput()
    .appendField(Blockly.Msg['PROCEDURES_DEFRETURN_TITLE'])
    .appendField(nameField, 'NAME')
    .appendField('(')
    .appendField('', 'PARAMS')
    .appendField(')  : ')
    .appendField(new Blockly.FieldDropdown([
      ['int', 'int'],
      ['float', 'float'],
      ['char', 'char']
    ], this.validate), 'RETURN_TYPE');
  this.appendValueInput('RETURN')
    .setAlign(Blockly.ALIGN_RIGHT)
    .appendField(Blockly.Msg['PROCEDURES_DEFRETURN_RETURN']);
  this.setMutator(new Blockly.Mutator(['procedures_mutatorarg']));
  if ((this.workspace.options.comments ||
    (this.workspace.options.parentWorkspace &&
      this.workspace.options.parentWorkspace.options.comments)) &&
    Blockly.Msg['PROCEDURES_DEFRETURN_COMMENT']) {
    this.setCommentText(Blockly.Msg['PROCEDURES_DEFRETURN_COMMENT']);
  }
  this.setStyle('procedure_blocks');
  this.setTooltip(Blockly.Msg['PROCEDURES_DEFRETURN_TOOLTIP']);
  this.setHelpUrl(Blockly.Msg['PROCEDURES_DEFRETURN_HELPURL']);
  this.arguments_ = [];
  this.argumentVarModels_ = [];
  this.setStatements_(true);
  this.statementConnection_ = null;
};

Blockly.Blocks['procedures_defreturn'].updateParams_ = Blockly.Blocks['procedures_defnoreturn'].updateParams_
Blockly.Blocks['procedures_defreturn'].compose = Blockly.Blocks['procedures_defnoreturn'].compose


// PARAMETERS
Blockly.Blocks['procedures_mutatorarg'].init = function () {
  const field = new Blockly.FieldTextInput(Blockly.Procedures.DEFAULT_ARG, this.validator_);
  field.oldShowEditorFn_ = field.showEditor_;
  const newShowEditorFn = function () {
    this.createdVariables_ = [];
    this.oldShowEditorFn_();
  };
  field.showEditor_ = newShowEditorFn;

  this.appendDummyInput()
    .appendField(field, 'NAME')
    .appendField(' : ')
    .appendField(new Blockly.FieldDropdown([
      ['int', 'int'],
      ['float', 'float'],
      ['char', 'char']
    ]), 'TYPE');
  this.setPreviousStatement(true);
  this.setNextStatement(true);
  this.setStyle('procedure_blocks');
  this.setTooltip(Blockly.Msg['PROCEDURES_MUTATORARG_TOOLTIP']);
  this.contextMenu = false;

  field.onFinishEditing_ = this.deleteIntermediateVars_;
  field.createdVariables_ = [];
  field.onFinishEditing_('x');
}

Blockly.Blocks['procedures_mutatorarg'].onchange = function () {
  if (this.getSurroundParent() !== null) {
    this.setEditable(false);
    this.setEnabled(false);
  }
  const varName = this.getFieldValue('NAME');
  this.setFieldValue(varName, 'NAME');
  if (this.getSurroundParent() === null) {
    const varType = this.getFieldValue('TYPE');
    let outerWs = Blockly.Mutator.findParentWs(this.workspace);
    let model = outerWs.getVariable(varName, varType);
    if (model) {
      let map = outerWs.getVariableMap();
      map.deleteVariableInternal(model, []);
    }
  }
}

Blockly.Blocks['procedures_mutatorarg'].validator_ = function (varName) {
  const sourceBlock = this.getSourceBlock();
  const outerWs = Blockly.Mutator.findParentWs(sourceBlock.workspace);
  varName = varName.replace(/[\s\xa0]+/g, ' ').replace(/^ | $/g, '');
  if (!varName) {
    return null;
  }
  // Prevents duplicate parameter names in functions
  const workspace = sourceBlock.workspace;
  const blocks = workspace.getAllBlocks(false);
  const caselessName = varName.toLowerCase();
  for (let i = 0; i < blocks.length; i++) {
    if (blocks[i].id === this.getSourceBlock().id) {
      continue;
    }
    // Other blocks values may not be set yet when this is loaded.
    const otherVar = blocks[i].getFieldValue('NAME');
    if (otherVar && otherVar.toLowerCase() === caselessName) {
      return null;
    }
  }
  if (sourceBlock.isInFlyout || sourceBlock.getSurroundParent() === null) {
    return varName;
  }
  let type = sourceBlock.getFieldValue('TYPE');
  let model = outerWs.getVariable(varName, type);
  if (model && model.name !== varName) {
    // Rename the variable (case change)
    outerWs.renameVariableById(model.getId(), varName);
  }
  if (!model) {
    model = outerWs.createVariable(varName, type);
    if (model && this.createdVariables_) {
      this.createdVariables_.push(model);
    }
  }
  return varName;
};

// FUNCTION CALL
Blockly.Blocks['procedures_callnoreturn'].setProcedureParameters_ = function (paramNames, paramIds) {
  const defBlock = Blockly.Procedures.getDefinition(this.getProcedureCall(), this.workspace);
  const mutatorOpen = defBlock && defBlock.mutator && defBlock.mutator.isVisible();
  if (!mutatorOpen) {
    this.quarkConnections_ = {};
    this.quarkIds_ = null;
  }
  if (!paramIds) {
    // Reset the quarks (a mutator is about to open).
    return;
  }
  // Test arguments (arrays of strings) for changes. '\n' is not a valid
  // argument name character, so it is a valid delimiter here.
  if (paramNames.join('\n') === this.arguments_.join('\n')) {
    // No change.
    this.quarkIds_ = paramIds;
    return;
  }
  if (paramIds.length !== paramNames.length) {
    throw RangeError('paramNames and paramIds must be the same length.');
  }
  this.setCollapsed(false);
  if (!this.quarkIds_) {
    // Initialize tracking for this block.
    this.quarkConnections_ = {};
    this.quarkIds_ = [];
  }
  // Switch off rendering while the block is rebuilt.
  const savedRendered = this.rendered;
  this.rendered = false;
  // Update the quarkConnections_ with existing connections.
  for (let i = 0; i < this.arguments_.length; i++) {
    let input = this.getInput('ARG' + i);
    if (input) {
      let connection = input.connection.targetConnection;
      this.quarkConnections_[this.quarkIds_[i]] = connection;
      if (mutatorOpen && connection &&
        paramIds.indexOf(this.quarkIds_[i]) === -1) {
        // This connection should no longer be attached to this block.
        connection.disconnect();
        connection.getSourceBlock().bumpNeighbours();
      }
    }
  }
  // Rebuild the block's arguments.
  this.arguments_ = [].concat(paramNames);
  // And rebuild the argument model list.
  const models = this.workspace.getAllVariables();
  this.argumentVarModels_ = [];
  for (let i = 0; i < this.arguments_.length; i++) {
    let model = models.find(x => {
      return x.name === this.arguments_[i];
    });
    let variable = Blockly.Variables.getOrCreateVariablePackage(
      this.workspace, null, this.arguments_[i], model.type);
    this.argumentVarModels_.push(variable);
  }
  this.updateShape_();
  this.quarkIds_ = paramIds;
  // Reconnect any child blocks.
  if (this.quarkIds_) {
    for (let i = 0; i < this.arguments_.length; i++) {
      let quarkId = this.quarkIds_[i];
      if (quarkId in this.quarkConnections_) {
        const connection = this.quarkConnections_[quarkId];
        if (!Blockly.Mutator.reconnect(connection, this, 'ARG' + i)) {
          // Block no longer exists or has been attached elsewhere.
          delete this.quarkConnections_[quarkId];
        }
      }
    }
  }
  // Restore rendering and show the changes.
  this.rendered = savedRendered;
  if (this.rendered) {
    this.render();
  }
}

Blockly.Blocks['procedures_callnoreturn'].updateShape_ = function () {
  for (var i = 0; i < this.arguments_.length; i++) {
    let field = this.getField('ARGNAME' + i);
    if (field) {
      Blockly.Events.disable();
      try {
        field.setValue(this.arguments_[i]);
      } finally {
        Blockly.Events.enable();
      }
    } else {
      // Add new input.
      field = new Blockly.FieldLabel(this.arguments_[i]);
      const input = this.appendValueInput('ARG' + i)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(field, 'ARGNAME' + i)
        .setCheck(this.argumentVarModels_[i].type);
      input.init();
    }
  }
  // Remove deleted inputs.
  while (this.getInput('ARG' + i)) {
    this.removeInput('ARG' + i);
    i++;
  }
  // Add 'with:' if there are parameters, remove otherwise.
  const topRow = this.getInput('TOPROW');
  if (topRow) {
    if (this.arguments_.length) {
      if (!this.getField('WITH')) {
        topRow.appendField(Blockly.Msg['PROCEDURES_CALL_BEFORE_PARAMS'], 'WITH');
        topRow.init();
      }
    } else {
      if (this.getField('WITH')) {
        topRow.removeField('WITH');
      }
    }
  }
}

Blockly.Blocks['procedures_callreturn'].onchange = function (event) {
  let def;
  let name;
  if (!this.workspace || this.workspace.isFlyout) {
    // Block is deleted or is in a flyout.
    return;
  }
  if (!event.recordUndo) {
    // Events not generated by user. Skip handling.
    return;
  }
  if (event.type === Blockly.Events.BLOCK_CREATE &&
    event.ids.indexOf(this.id) !== -1) {
    // Look for the case where a procedure call was created (usually through
    // paste) and there is no matching definition.  In this case, create
    // an empty definition block with the correct signature.
    name = this.getProcedureCall();
    def = Blockly.Procedures.getDefinition(name, this.workspace);
    if (def && (def.type !== this.defType_ ||
      JSON.stringify(def.getVars()) !== JSON.stringify(this.arguments_))) {
      // The signatures don't match.
      def = null;
    }
    if (!def) {
      Blockly.Events.setGroup(event.group);
      const xml = Blockly.utils.xml.createElement('xml');
      const block = Blockly.utils.xml.createElement('block');
      block.setAttribute('type', this.defType_);
      const xy = this.getRelativeToSurfaceXY();
      const x = xy.x + Blockly.SNAP_RADIUS * (this.RTL ? -1 : 1);
      const y = xy.y + Blockly.SNAP_RADIUS * 2;
      block.setAttribute('x', x);
      block.setAttribute('y', y);
      const mutation = this.mutationToDom();
      block.appendChild(mutation);
      const field = Blockly.utils.xml.createElement('field');
      field.setAttribute('name', 'NAME');
      field.appendChild(Blockly.utils.xml.createTextNode(
        this.getProcedureCall()));
      block.appendChild(field);
      xml.appendChild(block);
      Blockly.Xml.domToWorkspace(xml, this.workspace);
      Blockly.Events.setGroup(false);
    }
  } else if (event.type === Blockly.Events.BLOCK_DELETE) {
    // Look for the case where a procedure definition has been deleted,
    // leaving this block (a procedure call) orphaned.  In this case, delete
    // the orphan.
    name = this.getProcedureCall();
    def = Blockly.Procedures.getDefinition(name, this.workspace);
    if (!def) {
      Blockly.Events.setGroup(event.group);
      this.dispose(true);
      Blockly.Events.setGroup(false);
    }
  } else if (event.type === Blockly.Events.CHANGE && event.element === 'disabled') {
    name = this.getProcedureCall();
    def = Blockly.Procedures.getDefinition(name, this.workspace);
    if (def && def.id === event.blockId) {
      // in most cases the old group should be ''
      var oldGroup = Blockly.Events.getGroup();
      if (oldGroup) {
        console.log('Saw an existing group while responding to a definition change');
      }
      Blockly.Events.setGroup(event.group);
      if (event.newValue) {
        this.previousEnabledState_ = this.isEnabled();
        this.setEnabled(false);
      } else {
        this.setEnabled(this.previousEnabledState_);
      }
      Blockly.Events.setGroup(oldGroup);
    }
  } else if (event.type === Blockly.Events.CHANGE) {
    let name = this.getProcedureCall();
    let def = Blockly.Procedures.getDefinition(name, this.workspace);
    if (def && def.id === event.blockId) {
      let returnType = def.getFieldValue('RETURN_TYPE');
      this.setOutput(true, returnType);
    }
  }
}

Blockly.Blocks['procedures_callreturn'].setProcedureParameters_ = Blockly.Blocks['procedures_callnoreturn'].setProcedureParameters_;
Blockly.Blocks['procedures_callreturn'].updateShape_ = Blockly.Blocks['procedures_callnoreturn'].updateShape_;


// VARS
Blockly.Blocks['variable_declaration'] = {
  init: function() {
    this.appendDummyInput()
      .appendField("var")
      .appendField(new Blockly.FieldVariable("item"), "VAR");
    this.appendDummyInput("DIM1")
      .appendField("[")
      .appendField(new Blockly.FieldNumber(1, 1, Infinity, 1), "DIM1")
      .appendField("]");
    this.appendDummyInput("DIM1_BRACKET");
    this.appendDummyInput("DIM2")
      .appendField("[")
      .appendField(new Blockly.FieldNumber(1, 1, Infinity, 1), "DIM2")
      .appendField("]");
    this.appendDummyInput("DIM2_BRACKET");
    this.appendDummyInput()
      .appendField(":")
      .appendField("type", "TYPE");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(310);
    this.setTooltip("");
    this.setHelpUrl("");
    Blockly.Extensions.apply('contextMenu_variableDynamicSetterGetter', this, false);
  }
};

Blockly.Blocks['variables_set_dynamic'] = {
  init: function() {
    this.appendDummyInput()
      .appendField(new Blockly.FieldVariable("item"), "VAR")
    this.appendValueInput("DIM1")
      .appendField("[")
      .setCheck("int");
    this.appendDummyInput("DIM1_BRACKET")
      .appendField("]");
    this.appendValueInput("DIM2")
      .appendField("[")
      .setCheck("int");
    this.appendDummyInput("DIM2_BRACKET")
      .appendField("]");
    this.appendValueInput("VALUE")
      .appendField("=")
      .setCheck(null);
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(310);
    this.setTooltip("");
    this.setHelpUrl("");
    Blockly.Extensions.apply('contextMenu_variableDynamicSetterGetter', this, false);
  }
};

Blockly.Blocks['variables_get_dynamic'] = {
  init: function() {
    this.appendDummyInput()
      .appendField(new Blockly.FieldVariable("item"), "VAR")
    this.appendValueInput("DIM1")
      .appendField("[")
      .setCheck("int");
    this.appendDummyInput("DIM1_BRACKET")
      .appendField("]");
    this.appendValueInput("DIM2")
      .appendField("[")
      .setCheck("int");
    this.appendDummyInput("DIM2_BRACKET")
      .appendField("]");
    this.setInputsInline(true);
    this.setOutput(true, null);
    this.setColour(310);
    this.setTooltip("");
    this.setHelpUrl("");
    Blockly.Extensions.apply('contextMenu_variableDynamicSetterGetter', this, false);
  }
};

Blockly.Constants.VariablesDynamic.CUSTOM_CONTEXT_MENU_VARIABLE_GETTER_SETTER_MIXIN.onchange = function (_e) {
  const id = this.getFieldValue('VAR');
  const variableModel = Blockly.Variables.getVariable(this.workspace, id);
  let removeIndex;
  if (variableModel && variableModel.type.indexOf('array') !== -1) {
    this.getInput('DIM1').setVisible(true);
    this.getInput('DIM1_BRACKET').setVisible(true);
    this.getInput('DIM2').setVisible(false);
    this.getInput('DIM2_BRACKET').setVisible(false);
    removeIndex = 6;
  } else if (variableModel && variableModel.type.indexOf('matrix') !== -1) {
    this.getInput('DIM1').setVisible(true);
    this.getInput('DIM1_BRACKET').setVisible(true);
    this.getInput('DIM2').setVisible(true);
    this.getInput('DIM2_BRACKET').setVisible(true);
    removeIndex = 7;
  } else {
    this.getInput('DIM1').setVisible(false);
    this.getInput('DIM1_BRACKET').setVisible(false);
    this.getInput('DIM2').setVisible(false);
    this.getInput('DIM2_BRACKET').setVisible(false);
  }
  if (this.type === 'variables_set_dynamic') {
    this.moveInputBefore('VALUE');
    this.getInput('VALUE').setCheck(variableModel.type.slice(removeIndex));
  } else if (this.type === 'variables_get_dynamic') {
    this.setOutput(true, variableModel.type.slice(removeIndex));
  } else {
    this.setFieldValue(variableModel.type.slice(removeIndex), "TYPE");
  }
}

// This is to change value of default generated by for loop to int
Blockly.FieldVariable.prototype.setTypes_ = function(opt_variableTypes, opt_defaultType) {
  let variableTypes;
  const defaultType = opt_defaultType || 'int';
  if (opt_variableTypes === null || opt_variableTypes === undefined) {
    variableTypes = null;
  } else if (Array.isArray(opt_variableTypes)) {
    variableTypes = opt_variableTypes;
    let isInArray = false;
    for (var i = 0; i < variableTypes.length; i++) {
      if (variableTypes[i] === defaultType) {
        isInArray = true;
      }
    }
    if (!isInArray) {
      throw Error('Invalid default type \'' + defaultType + '\' in ' +
        'the definition of a FieldVariable');
    }
  } else {
    throw Error('\'variableTypes\' was not an array in the definition of ' +
      'a FieldVariable');
  }
  this.defaultType_ = defaultType;
  this.variableTypes = variableTypes;
};
