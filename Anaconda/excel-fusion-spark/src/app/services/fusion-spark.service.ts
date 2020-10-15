import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class FusionSparkService {
  protected httpOptions: object = {
    headers: new HttpHeaders(
      { 'Content-Type': 'application/json' }
    )
  };
  protected baseUrl = 'https://localhost:8081';
  protected defaultQueryParams: Object = {
    params: {
      tag: 'all'
    }
  };

  constructor(
    public http: HttpClient
  ) { }

  checkForParams(params: object, catalogue?: string): object {
    let q = {};

    if (Object.entries(params).length === 0 && params.constructor === Object) {
      q = { ...this.httpOptions, ...this.defaultQueryParams};
    } else {
      q = { ...q, ...this.defaultQueryParams };
    }

    if (catalogue) {
      q['params']['catalogue'] = catalogue;
    }

    return q;
  }
}
