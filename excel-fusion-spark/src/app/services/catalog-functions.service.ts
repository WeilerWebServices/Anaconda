import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { FusionSparkService } from './fusion-spark.service';

// https://localhost:8081/api/v1.0/functions/?tag=all
const functionAPIBase = '/api/v1.0/functions/';

@Injectable({
  providedIn: 'root'
})
export class CatalogFunctionsService extends FusionSparkService {

  constructor(
    public http: HttpClient
  ) { 
    super(http);
  }

  getFunctions(params: object) {
    const q = this.checkForParams(params);
    return this.http.get(`${this.baseUrl}${functionAPIBase}`, q);
  }

  getFunctionDetails(params: object, catalogue?: string) {
    let q = this.checkForParams(params, catalogue);
    return this.http.get(`${this.baseUrl}${functionAPIBase}`, q);
  }

  getFunctionsFromCatalogue(params: object, catalogue?: string) {
    let q = this.checkForParams(params, catalogue);
    return this.http.get(`${this.baseUrl}${functionAPIBase}`, q);
  }

  postFunctionForm(baseUrl: string, formData: object, params: object) {
    return this.http.post(`${baseUrl}`, formData, this.httpOptions);
  }

}
