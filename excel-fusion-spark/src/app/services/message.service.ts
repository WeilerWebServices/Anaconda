import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  private subject = new Subject<any>();

  constructor() { }

  sendSearchableFunctions(data: any) {
    this.subject.next(data);
  }

  getSearchableFunctions(): Observable<any> {
    return this.subject.asObservable();
  }

  clear() {
    this.subject.next();
  }
}
