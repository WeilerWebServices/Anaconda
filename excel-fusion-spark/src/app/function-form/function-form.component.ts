import { Component, OnInit, Input, EventEmitter, ViewContainerRef, ChangeDetectorRef, Output } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CatalogFunctionsService } from '../services/catalog-functions.service';
import { FormBuilder, FormGroup, FormControl } from '@angular/forms';
import { MessageService } from '../services/message.service';
import { FunctionInputOutputService } from '../services/function-input-output.service';
import { getDataFromRange, writeOnSelectedCell } from '../excel';

@Component({
  selector: 'app-notebook',
  templateUrl: './function-form.component.html',
  styleUrls: ['./function-form.component.scss']
})
export class FunctionFormComponent implements OnInit {
  selectedCatalogFunctionName: string;
  selectedCatalogFunctionObject: object;
  allCatalogFunctions: Array<any>;
  projectForm: FormGroup;
  excelSync: boolean = true;
  autoRun: boolean = false;
  functionFormGroup: FormGroup;
  hasInputs: boolean = false;
  hasErrors: boolean = false;
  errorMessage: string = '';
  isOutputLoading: boolean = false;
  hasPostFired: boolean = false;
  // outputData: any;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private service: CatalogFunctionsService,
    private fb: FormBuilder,
    private ref: ChangeDetectorRef,
    private fio: FunctionInputOutputService
  ) {
    this.selectedCatalogFunctionName = this.route.snapshot.params.name;
    this.functionFormGroup = new FormGroup({});
    this.hasErrors = false;
  }

  ngOnInit() {
    // this.service.getFunctionDetails({}, this.selectedCatalogFunctionName).subscribe((catalogFunctions) => {
    this.service.getFunctions({}).subscribe((catalogFunctions) => {
      let tmp = [];
      // TODO: Fabio & Rudy are getting different data so data extraction is a bit different for each of us.
      // Fabio: L41 - Object.values(catalogFunctions).forEach((v) => {
      // Rudy:  L41 - Object.values(catalogFunctions)[0].forEach((v) => {
      if (catalogFunctions[0] instanceof Array){
        catalogFunctions = catalogFunctions[0]
      }
      Object.values(catalogFunctions).forEach((v) => {
        if (v.name === this.selectedCatalogFunctionName) {
          this.selectedCatalogFunctionObject = v;
        }
        tmp.push(v.name);
      });

      this.allCatalogFunctions = tmp;
      this.createForm();
    });
  }

  createForm() {
    // tslint:disable-next-line: max-line-length
    console.log('create form for function... ')
    console.log('this.selectedCatalogFunctionObject: ', this.selectedCatalogFunctionName);
    console.log('this.selectedCatalogFunctionObject[meta]: ', this.selectedCatalogFunctionName['meta']);

    if (this.selectedCatalogFunctionObject && this.selectedCatalogFunctionObject['meta'] && this.selectedCatalogFunctionObject['meta'].inputs) {
      this.hasInputs = true;
      this.selectedCatalogFunctionObject['meta'].inputs.forEach((field) => {
        this.functionFormGroup.addControl(field.name, new FormControl());
      });
    }
  }

  excelSyncToggle(): void {
    this.excelSync = !this.excelSync;
  }

  autoRunToggle(): void {
    this.autoRun = !this.autoRun;
  }

  handleOutputLoading() {
    this.isOutputLoading = !this.isOutputLoading;
  }

  toggleHasPostFired() {
    this.hasPostFired = !this.hasPostFired;
  }

  resolveParams(baseUrl: string, formData: object, params: object) {
    if (Object.keys(formData).length == Object.keys(params).length){
      return this.doSubmit(baseUrl, params)
    } else {
      for (let key in formData) {
        if ( params[key] == null && formData[key] !== null ){
          if ( formData[key].startsWith('=') ){
            var _params = params;
            var _baseUrl = baseUrl;
            var _formData = formData;
            var _this = this;
            var excelCallback = (resultRange: any) : void => {
              var newParams = _params;
              newParams[key] = resultRange.values;
              _this.resolveParams(_baseUrl, _formData, newParams);
            }
            getDataFromRange(formData[key].slice(1), excelCallback)
          }else{
            params[key] = formData[key];
            this.resolveParams(baseUrl, formData, params)
          }
        }
      }
      if (Object.keys(params).length == 0){
        return this.doSubmit(baseUrl, params);
      }
    }

    // return this.http.post(`${baseUrl}`, formData, this.httpOptions);
  }

  doSubmit(baseUrl: string, params: object) {
    this.service.postFunctionForm(
      this.selectedCatalogFunctionObject['url'],
      params,
      {}
    ).subscribe((data) => {
      this.handleOutputLoading();
      // TODO: Fully implement later
      // this.fio.sendOutputDataToChild(data);

      var outputDivHtml = '<div>';
      var outputDiv = document.getElementsByClassName('function-form-response')[0];
      if (data['display_data'] != null){
        // @Rudy - This is Fabio's crappy quick ugly hack... look elsewhere ;)
        outputDivHtml += '<div><img src="data:image/png;base64,'+data['display_data']['image/png']+'"</div>';
      }

      if (data['result'] != null){
        // @Rudy - more ugly hacks... or at least I hope Angular has better suppoort for this lol
        // outputDivHtml += '<div>'+data['result']+'"</div>';
        try{
          // var resultData = JSON.parse(data['result']);
          var resultData = JSON.parse(JSON.parse(data['result']))
        }catch{
          try{
            var resultData = JSON.parse(data['result']);
          }catch{
            var resultData = data['result'];
          }
        }
        writeOnSelectedCell(resultData);
      }

      outputDivHtml += '</div>';
      outputDiv.innerHTML = outputDivHtml;
    }, (error) => {
      this.hasErrors = true;
      this.errorMessage = error.message;
      // this.ref.detectChanges();
    });
  }

  onSubmit() {
    if (!this.hasPostFired) {
      this.toggleHasPostFired();
      this.resolveParams(
        this.selectedCatalogFunctionObject['url'],
        this.functionFormGroup.value,
        {}
      );
    }
  }
}
