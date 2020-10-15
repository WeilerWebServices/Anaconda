import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FunctionInputOutputService {
  private subject = new Subject<any>();

  constructor() { }

  sendOutputDataToChild(data: any) {
    this.subject.next(data);
  }

  getOutputDataFromParent(): Observable<any> {
    return this.subject.asObservable();
  }
}
