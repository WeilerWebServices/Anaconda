import { Component, OnInit, EventEmitter, Input } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { debounceTime, distinctUntilChanged, filter, tap, map} from 'rxjs/operators';
import { MessageService } from '../services/message.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {
    searchPlaceholder: string = 'Search for functions';
    onForm: boolean = false;
    dataSet: any;
    loading: boolean;
    //
    message: any; // searchableFunctions
    subscription: Subscription;

    constructor(
      private router: Router,
      private route: ActivatedRoute,
      private messageService: MessageService
    ) {
      // TODO: Use search placeholder to display functions.
      // May not be best option per UI because form already has ng-select.
      // const href = window.location.href;
      // const hrefArr = href.split('/');
      // const last = hrefArr[hrefArr.length - 1];
      // if (last !== 'functions') {
      //   this.onForm = true;
      //   this.searchPlaceholder = last;
      // }
    }

    ngOnInit() {
      this.subscription = this.messageService
          .getSearchableFunctions()
          .subscribe((message) => {
            console.log('search component::subscripted to getSearchableFunctions: ', message);
            this.dataSet = message;
          });
    }

    goToDetail(item) {
      this.router.navigate(['functions', item.name]);
    }

}
