// var namespace = require("./namespace.js");
// var axl = namespace.axl;

// var code_block = require("./code_block.js");
// var log = require("../axl/log.js");


var NUMBER_PATTERN = /\d+/g;

function highlight (rangeAddress, color){
  Excel.run(function (ctx) {
      var sheetName = "Sheet1";
      var range = ctx.workbook.worksheets.getItem(sheetName).getRange(rangeAddress);

      range.format.fill.color = color;
      return ctx.sync().then(function () {
          var vals = range.values;
      });
  }).catch(function (error) {
      console.log("Error: " + error);
      if (error instanceof OfficeExtension.Error) {
          console.log("Debug info: " + JSON.stringify(error.debugInfo));
      }
  });
}

function getAddressObj(rangeAddress){
  var sheetName;
  if (rangeAddress.indexOf("!")>-1){
    sheetName = rangeAddress.split("!")[0];
    rangeAddress = rangeAddress.split("!")[1];
  }
  rangeAddress = rangeAddress.toUpperCase();
  var firstCell = rangeAddress.split(":")[0];

  return {sheet: sheetName, address: rangeAddress, firstCell: firstCell};
}

function getDataFromRange(rangeAddress, callback, errorCallback) {
  var addr = getAddressObj(rangeAddress);
  
  Excel.run(function (ctx) {
      var _addr = addr
      var worksheet;
      if (addr.sheet !== undefined){
        worksheet = ctx.workbook.worksheets.getItem(addr.sheet);
      } else {
        worksheet = ctx.workbook.worksheets.getActiveWorksheet();
      }
      // console.log(excel.getDataFromRange("Sheet1!B1:C4", function(a){console.log(a);}))
      console.log("ASKING FOR ", addr.address);
      var sheetName = "Sheet1";
      var range = worksheet.getRange(addr.address);
      range.load('values');
      range.load('address');
      range.load('formulas');
      return ctx.sync().then(function () {
        _addr.values = range.values;
        _addr.formulas = range.formulas;

        callback(_addr);
      });
  }).catch(function (error) {
      console.log("Errosr: ", error);
      if (error instanceof OfficeExtension.Error) {
          console.log("Debug info: " + JSON.stringify(error.debugInfo));
      }
  });
}

function read_from_binding(binding, callback){
  // reads from a binding object by calling the binding.getDataAsync and passing
  // the result.value and result objects to callback. It also updates the global
  // variables namespace (axl.namespace) with the updated values so variables in that
  // namespace are always in sync

  //TODO(fpliger): it'd be better to get the namesapce as arg so it easier to test
  //              and more flexible
  var name = binding.id;
  var _callback = callback;
  function read_from_binding_cb(result) {
    var rangeObj = getAddressObj(binding.id.replace("_TO_", ":"));
    rangeObj.values = result.value;

    update_namespace(name, rangeObj);
    if (_callback!==undefined){
      callback(rangeObj, result);
    }
  }
  binding.getDataAsync(read_from_binding_cb);
}

function range_cb(AsyncResult) {
  read_from_binding(AsyncResult.binding);
}

function range_cb_factory(callback){
  function range_cb(AsyncResult) {
    read_from_binding(AsyncResult.binding, callback);
  }
  return range_cb;
}

function createNewRange(){
  var range_name = $("#get-range-input").val();
  if (range_name !== undefined | range_name !== ""){
    _getRangeFromName(range_name);
  }else{
    _getRangeFromPrompt();
  }
}
// TODO: Unused but probably useful when we better support range selections from the UI
// function getRangeFromPrompt(){
//     Office.context.document.bindings.addFromPromptAsync( //Office.BindingType.Matrix
//       Office.BindingType.Table, { id: 'myBinding' }, function (asyncResult) {
//       if (asyncResult.status == Office.AsyncResultStatus.Failed) {
//           console.log('Action failed. Error: ' + asyncResult.error.message);
//       } else {
//           console.log('Added new binding with type: ' + asyncResult.value.type + ' and id: ' + asyncResult.value.id);
//
//           Office.select("bindings#myBinding").addHandlerAsync(
//             Office.EventType.BindingDataChanged, range_cb);
//       }
//   });
// }

function add_var_to_namespace(name, address){
  if (axl.namespace.indexOf(name)>=-1){
    axl.namespace[name] = {"name": name, "value": null, "callbacks": [], "address": address};
  }
}

function update_namespace(name, value){
  if (axl.namespace[name]!==undefined){
    axl.namespace[name].value = value;
  }


  // now we should call the callbacks registered on this range
  // var cbs = axl.namespace[name].callbacks;
  // if (cbs.length > 0){
  //   for (var i=0; i<cbs.length; i++){
  //     console.log("EXECUTING CALLBACK " + name + " index " + i);
  //     _execute_code(cbs[i]);
  //   }
  // }
}

function getRangeFromName(address, callback, nameId, errorCallback){
  // only get range if it's not in the namespace already
  console.log("getting name from", address, nameId)
  if (nameId === undefined){
    nameId = address
  }
  if (!(nameId in axl.namespace)){
    Office.context.document.bindings.addFromNamedItemAsync(
      address, Office.BindingType.Matrix, {id: nameId}, function (result) {
        if (result.status == 'succeeded'){
          var new_cb = range_cb_factory(callback);
          var new_binding = Office.select("bindings#" + nameId);
          new_binding.addHandlerAsync(Office.EventType.BindingDataChanged, new_cb);
          add_var_to_namespace(nameId, address);

          // read from binding range
          read_from_binding(result.value, callback);
        }else{
          var errObj = {
            nameId: nameId,
            address: address,
            errorCode: result.error.code,
            errorName: result.error.name,
            errorMessage: result.error.message
          }
          console.log('ERROR while getting name '+ nameId + ' . MSG: [' + result.error.code + "] " + result.error.name + " " + result.error.message);
          if (errorCallback!==undefined){
              errorCallback(errObj);
          }

        }
    });
  }else{
    // value is already in fusion namespace so let's use it
    // console.log("REUSINGGGGG!!!!!!", axl.namespace[nameId]);
    callback(axl.namespace[nameId].value)
  }
}

// function write_on_selected_cell(values){
//   // Write values to the selected range in the active notebook using the native
//   // setSelectedDataAsync.
//   // NOTE: THIS METHOD WON'T WORK IF THE SELECTED CELL/RANGE HAVE CONTENT ON IT
//   //       USE 'writeOnSelectedCell' INSTEAD!
//   Office.context.document.setSelectedDataAsync(
//     values,
//     {},// tableOptions,
//     function (asyncResult) {
//       if (asyncResult.status == "failed") {
//         //log.log("Action failed with error: " + asyncResult.error.message, log.level.ERROR);
//         console.log("Action failed with error: " + asyncResult.error.message);
//       } else {
//         //log.log("Check out your new table, then click next to learn another API call.", log.level.ERROR);
//         console.log("Check out your new table, then click next to learn another API call.");
//       }
//     }
//   );
// }

function writeOnSelectedCell(values, errorCallback){
  Excel.run(function (ctx) {
    var selectedRange = ctx.workbook.getSelectedRange().load();
    var _values = values;


    var _eCB = errorCallback;

    return ctx.sync().then(function() {
      var _addr = selectedRange.address.split("!");
      console.log("Detected range from selection: " + selectedRange.address);

      return write_on_range(_values, _addr[1], _addr[0], errorCallback);
    });
  }).catch(function(error) {
      // log.log("Error Executing writeOnSelectedCell: " + error, log.level.ERROR);
      console.log("Error Executing writeOnSelectedCell: " + error);//, log.level.ERROR);
   });
}

function writeOnNamedRange(values, name, errorCallback){
  Excel.run(function (ctx) {
  	var namedRange = ctx.workbook.names.getItem(name).getRange();
    var _values = values;
    namedRange.load("address");
  	return ctx.sync().then(function () {
      var _addr = namedRange.address.split("!");
      return write_on_range(_values, _addr[1], _addr[0], errorCallback);
  	});
  }).catch(function(error) {
    //log.log("Error Executing writeOnNamedRange: " + error, log.level.ERROR);
   });
}

function write_on_range(value, rangeAddress, sheetName, errorCallback, formulas){
  rangeAddress = rangeAddress.toUpperCase();
  var firstCell = rangeAddress.split(":")[0];
  var vObj;
  var numberFormat;
  // if (value.values !== undefined){
  //   vObj = value;
  //   value = vObj.values;
  //   if (vObj.dtypes !== undefined){
  //     numberFormat = vObj.dtypes;
  //   }
  // }
  var fittingRange = getRangeToFit(value, firstCell);

  console.log("WR ", value, rangeAddress);

  // var res = intersectInNamespace(rangeAddress);
  // if (res.intersects===true){
  //   errorCallback("Value not being written to excel due to collision detection. Details: \n\n" + res.details);
  //   console.log("Value not being written to excel due to collision detection. Details: \n\n" + res.details);
  //   return;
  // }

  Excel.run(function (ctx) {
      var worksheet;
      if (sheetName !== undefined){
        worksheet = ctx.workbook.worksheets.getItem(sheetName);
      } else {
        worksheet = ctx.workbook.worksheets.getActiveWorksheet();
      }
      var range = worksheet.getRange(fittingRange);
      range.values = value;

      if (numberFormat !== undefined){
          console.log("Number format detected: ", numberFormat);
          range.numberFormat = numberFormat;
      }

      if (formulas!==formulas){
        range.formulas = formulas;
      }
      // TODO FUSION-NEXT-GEN: we need another way to track active fusion formulas and uncomment the code below
      // var activeFormula = window.fusionActiveFormulas[firstCell];
      // if (activeFormula !== undefined){
      //   // TODO: we need to apply this to all cells inside the fittingRange not only to the first cell!
      //   // range.formulas = window.fusionActiveFormulas[firstCell];
      //   if (activeFormula[0][0] !== ""){
      //     var formulaCell = worksheet.getRange(firstCell);
      //     formulaCell.format.fill.color = '#FCFCCD';
      //   }
      // }
      range.load('text');
      return ctx.sync().then(function() {
          // TODO(fpliger): a flag to turn debug on/off and write successful wr here would be helpful
      });
  }).catch(function(error) {

  //log.log("Error: " + error, log.level.ERROR);
  if (error instanceof OfficeExtension.Error) {
      //log.log("Debug info: " + JSON.stringify(error.debugInfo));
  }
  });
}

function highlight_range(rangeAddress, sheetName, color, formulas){
  rangeAddress = rangeAddress.toUpperCase();
  Excel.run(function (ctx) {
      var worksheet;
      if (sheetName !== undefined){
        worksheet = ctx.workbook.worksheets.getItem(sheetName);
      } else {
        worksheet = ctx.workbook.worksheets.getActiveWorksheet();
      }
      var range = worksheet.getRange(rangeAddress);
      range.format.fill.color = (color === undefined) ? '#FCFCCD' : color;

      if (formulas!==formulas){
        range.formulas = formulas;
      }
      return ctx.sync().then(function() {
          // TODO(fpliger): a flag to turn debug on/off and write successful wr here would be helpful
      });
  }).catch(function(error) {
    //log.log("Error during range highlight: " + error, log.level.ERROR);
    if (error instanceof OfficeExtension.Error) {
        //log.log("Debug info: " + JSON.stringify(error.debugInfo));
    }
  });
}
//
// function addFormulaOnRange(formula, rangeAddress, sheetName, errorCallback){
//   console.log("ADDING FORMULA ON RANGE", rangeAddress);
//   rangeAddress = rangeAddress.toUpperCase();
//   var firstCell = rangeAddress.split(":")[0];
//   // var fittingRange = getRangeToFit(value, firstCell);
//
//   // var res = intersectInNamespace(rangeAddress);
//   if (res.intersects===true){
//     errorCallback("Value not being written to excel due to collision detection. Details: \n\n" + res.details);
//     console.log("Value not being written to excel due to collision detection. Details: \n\n" + res.details);
//     return;
//   }
//
//   Excel.run(function (ctx) {
//       var worksheet;
//       if (sheetName !== undefined){
//         worksheet = ctx.workbook.worksheets.getItem(sheetName);
//       } else {
//         worksheet = ctx.workbook.worksheets.getActiveWorksheet();
//       }
//       console.log("DOING!", formula)
//       var formulaCell = worksheet.getRange(firstCell);
//       formulaCell.formulas = formula;
//
//       formulaCell.load('text');
//       return ctx.sync().then(function() {
//           // TODO(fpliger): a flag to turn debug on/off and write successful wr here would be helpful
//       });
//   }).catch(function(error) {
//
//   //log.log("Error: " + error, log.level.ERROR);
//   if (error instanceof OfficeExtension.Error) {
//       //log.log("Debug info: " + JSON.stringify(error.debugInfo));
//   }
//   });
// }

// Reads data from current document selection and displays a notification
function getDataFromSelection(callback, errorCallback) {
    Office.context.document.getSelectedDataAsync(Office.CoercionType.Matrix,
        function (result) {
            console.log("RESULT FROM SELECTION", result);
            if (result.status === Office.AsyncResultStatus.Succeeded) {
                var rangeObj = getAddressObj(window.lastSelectedAddr);
                rangeObj.values = result.value;
                console.log(" --------------- CREATED NEW RANGE", rangeObj);
                callback(rangeObj, result);
            } else {
                errorCallback(result.error, result);
            }
        }
    );
}
var NUMBER_PATTERN = /\d+/g;
function getCellRow(cell){
  return parseInt(cell.match(NUMBER_PATTERN));
}

function getCellCol(cell){
  return cell.replace(NUMBER_PATTERN, '');
}

function indexToColumn(n) {
     var ordA = 'A'.charCodeAt(0);
     var ordZ = 'Z'.charCodeAt(0);
     var len = ordZ - ordA + 1;

     var s = "";
     while(n >= 0) {
         s = String.fromCharCode(n % len + ordA) + s;
         n = Math.floor(n / len) - 1;
     }
     return s;
 }

function columnToIndex(val) {
   var base = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', i, j, result = 0;

   for (i = 0, j = val.length - 1; i < val.length; i += 1, j -= 1) {
     result += Math.pow(base.length, j) * (base.indexOf(val[i]) + 1);
   }

   return result;
}

function isRange(r1) {
  return (r1.indexOf(":") === -1) ? false : true;
}

function intersectRanges(r1, r2) {
  if (r1 == r2) return true;

  var r1IsRange = isRange(r1);
  var r2IsRange = isRange(r2);
  // if they are both cells and we checked they are !== then they can't collide
  if (r1IsRange === false & r2IsRange === false) return false

  if (r1IsRange === false || r2IsRange === false){
    // _intersectCell(range, cell)
    return _intersectCell(rangeToRect(r2), rangeToRect(r1));
  }

  return _intersectRanges(rangeToRect(r1), rangeToRect(r2));
}

function intersectCell(r1, c1){
  return _intersectRanges(rangeToRect(r1), rangeToRect(c1));
}

function _intersectRanges(r1, r2) {
  return !(r2.left > r1.right ||
           r2.right < r1.left ||
           r2.top > r1.bottom ||
           r2.bottom < r1.top);
}

function _intersectCell(r1, c1){
  if (r1.left === undefined && r1.column !== undefined && c1.left !== undefined && c1.column === undefined){
    //in this case arguments are flipped... let's switch
    return _intersectCell(c1, r1);
  }
  return (r1.left <= c1.column && r1.right >= c1.column && r1.top <= c1.row && r1.bottom >= c1.row);
}

function intersectInNamespace(range, lNamespace){
  if (lNamespace===undefined){
    lNamespace = axl.namespace;
  }
  var ro;
  var res;
  for (var r in lNamespace){
    ro = lNamespace[r];
    if (ro.address!==undefined){
      res = intersectRanges(range, ro.address);
      if (res===true) return {intersects: res, details: "Range " + range + " intersects range in namespace: " + r};
      }
    }
  return {intersects: false, details: "Range " + range + " does not intersect other ranges in namespace"};
}

function rangeToRect(rangeAddress){
  rangeAddress = rangeAddress.toUpperCase();
  var rSplit = rangeAddress.split(":")
  var firstCell = rSplit[0];
  var lastCell = rSplit[1];

  var fCell = {
    row: getCellRow(firstCell),
    column: columnToIndex(getCellCol(firstCell))
  }

  if (lastCell===undefined){
    return fCell;
  }

  var lCell = {
    row: getCellRow(lastCell),
    column: columnToIndex(getCellCol(lastCell))
  };

  var rect = {
    left:   Math.min(fCell.column, lCell.column),
    top:    Math.min(fCell.row, lCell.row),
    right:  Math.max(fCell.column, lCell.column),
    bottom:  Math.max(fCell.row, lCell.row)
  };
  return rect;
}

function getRangeToFit(value, firstCell){
  var firstCellCol = getCellCol(firstCell);
  var firstCellRow = getCellRow(firstCell);
  var colsStartIndex = columnToIndex(firstCellCol);
  var colsEndIndex = colsStartIndex + value[0].length - 2; // -2 since we cound from starting index 1 and the +1 for incluse length
  var lastCol = indexToColumn(colsEndIndex);

  console.log(firstCellCol, colsStartIndex, indexToColumn(colsStartIndex))

  var lastRow = firstCellRow + value.length - 1;
  var lastCell = lastCol + lastRow;
   if (firstCell === lastCell){
     return firstCell;
   }else{
    var finalRange = firstCell + ":" + lastCell;
    return finalRange
   }
}


function highlightFormulas(formulasNamespace){
  for (var cell in formulasNamespace){
    var formulas = formulasNamespace[cell];
    if (formulas[0][0].substring(0, 1)==="="){
      highlight_range(cell, formulas);
    }
  }
}

function addEventHandlerToDocument(MyHandler) {

  var prevRange;
  if (window.fusionSelectionHistory===undefined){
    window.fusionSelectionHistory = [];

    // retrieve formulas saved on the last session
    var savedFormulas = Office.context.document.settings.get("fusion_formulas")

    // set the global fusion active formulas
    window.fusionActiveFormulas = (savedFormulas) ? JSON.parse(savedFormulas) : {};

    highlightFormulas(window.fusionActiveFormulas);
  }

  // we need a wrapper function for the received callback because the async nature
  // of office.js won't let us just pass the callback itself. We need to add a layer
  // so the callback is agnostic of everything and just gets the select address,
  // values and formulas
  function _wrap(eventArgs){
    var _pr = prevRange;
    var _mr = MyHandler;
    Excel.run(function (ctx) {
      var selectedRange = ctx.workbook.getSelectedRange().load("address");
      var __mr = _mr;
      var __pr = _pr;

      return ctx.sync().then(function() {
        // assign the previous lastSelectedAddr to the current previous
        window.prevSelectedAddr = window.lastSelectedAddr;
        var _addr = selectedRange.address.split("!");

        // only get data from range if there is actually something selected
        if (window.lastSelectedAddr!== undefined){
          getDataFromRange(window.lastSelectedAddr, __mr);
        }
        window.lastSelectedAddr = _addr[1];
      });
    }).catch(function(error) {
        //log.log("Error Executing READSelectedCell: " + error, log.level.ERROR);
     });
  }

    Office.context.document.addHandlerAsync(Office.EventType.DocumentSelectionChanged, _wrap);
}

function formulaBarCallback(rangeObj){ //rangeAddress, result, formulas) {
    // callback function to be used when the excel selection changes
    // so we can verify if the last cell edited had formulas and if
    // they failed in excel (so we can check if they exist in the
    // fusion namespace)
    var rangeAddress = rangeObj.address, result = rangeObj.values, formulas = rangeObj.formulas;
    console.log("Detected address,  prevSelectedAddr, lastSelectedAddr:", rangeAddress, window.prevSelectedAddr, window.lastSelectedAddr);

    if (window.fusionSelectionHistory.length>0){
      console.log("Previous address in hist", window.fusionSelectionHistory[window.fusionSelectionHistory.length-1]);
    }else{
      // this is the first cell selection in excel, so we can't really execute anything yet
    }

    // console.log("Detected result " + result);
    // console.log("Formulas " + formulas);

    // TODO(fpliger): only proceed if result === "?NAME" and formulas.length === 1
    //                to not interfere with excel execution chain (and user
    //                excel formulas)
    window.fusionSelectionHistory.push({address: rangeAddress, result: result, formulas: formulas});

    if (window.fusionActiveFormulas[window.lastSelectedAddr] !== undefined){
      // TODO: we need to apply this to all cells inside the fittingRange not only to the first cell!
      // range.formulas = window.fusionActiveFormulas[firstCell];
      // addFormulaOnRange(window.fusionActiveFormulas[window.lastSelectedAddr], window.lastSelectedAddr);
      console.log("restoring formulast to ", window.lastSelectedAddr, window.fusionActiveFormulas[window.lastSelectedAddr]);
      write_on_range(window.fusionActiveFormulas[window.lastSelectedAddr], window.lastSelectedAddr, undefined, undefined, window.fusionActiveFormulas[window.lastSelectedAddr])
    }

    var cb = new code_block.CodeBlock(window.activeEngine);

    // since formulas in excel matches the data format (array of arrays) we need
    // to access the first cell,
    console.log("FIX CODE FIRST " + formulas.length + " ---> " + formulas[0]);
    if (formulas[0] !== undefined & formulas[0][0].length > 0){
      if (formulas[0][0].substring(0, 1)==="=" & result[0][0] === "#NAME?"){
        window.fusionActiveFormulas[rangeAddress] = [[formulas[0][0]]];

        console.log("SAVING ACTIVE FORMULAS!!");
        // TODO: Need a better way of storing the session and the session namespace
        Office.context.document.settings.set("fusion_formulas", JSON.stringify(window.fusionActiveFormulas));

        Office.context.document.settings.saveAsync(function(asyncResult){
          console.log("Saved settings with status", asyncResult.status);}
        )
        console.log("DONE!");
        // TODO: missing spreadsheetname reference
        highlight_range(rangeAddress);

        var code = code_block.fuseFormula(formulas[0][0].substring(1));

        console.log("EXECUTING CB " + code.code);
        var serialize = false;
        var fooName = code.code.split("(")[0].trim();

        console.log("getting function", fooName);

        if (window.activeEngine.session.fusion_functions !== undefined){
          var currFoo = window.activeEngine.session.fusion_functions[fooName];
          if (currFoo !== undefined && currFoo.serialize !== undefined){
            serialize = currFoo.serialize;
          }
          window.formulaBarExec = window.prevSelectedAddr;
          cb.execute(code.code, serialize);
        }else{
          //TODO: We should intentionally manage this case, either with just FEEDBACK or preloading the namespaces!
        }
      }

    }
}

function get_url(){
  // case of Fusion running outside Excel
  if (Office.context.document === undefined){
    return "global"
  }else{
    // case of an anonymous spreadsheet not saved
    if (!Office.context.document.url) return "global";

    return Office.context.document.url;
  }
}

module.exports.highlight = highlight;
module.exports.getDataFromRange = getDataFromRange;
module.exports.read_from_binding = read_from_binding;

module.exports.range_cb = range_cb;
module.exports.createNewRange = createNewRange;
module.exports.getDataFromSelection = getDataFromSelection;
// module.exports.getRangeFromPrompt = getRangeFromPrompt;
module.exports.getRangeFromName = getRangeFromName;
// module.exports.write_on_selected_cell = write_on_selected_cell;
module.exports.write_on_range = write_on_range;
module.exports.writeOnSelectedCell = writeOnSelectedCell;
module.exports.writeOnNamedRange = writeOnNamedRange;
module.exports.addEventHandlerToDocument = addEventHandlerToDocument;
module.exports.formulaBarCallback = formulaBarCallback;
module.exports.get_url = get_url;
module.exports._intersectRanges = _intersectRanges;
module.exports._intersectCell = _intersectCell;
module.exports.intersectCell = intersectCell;
module.exports.rangeToRect = rangeToRect;
module.exports.columnToIndex = columnToIndex;
module.exports.getCellCol = getCellCol;
module.exports.getCellRow = getCellRow;
module.exports.getRangeToFit = getRangeToFit;
module.exports.intersectInNamespace = intersectInNamespace;
module.exports.isRange = isRange;
module.exports.getAddressObj = getAddressObj;
module.exports.range_cb_factory = range_cb_factory;
module.exports.add_var_to_namespace = add_var_to_namespace;
module.exports.update_namespace = update_namespace;
module.exports.highlight_range = highlight_range;