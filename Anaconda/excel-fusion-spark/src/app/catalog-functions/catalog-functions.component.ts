import { Component, OnInit, ViewContainerRef, NgZone, Renderer2 } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CatalogFunctionsService } from '../services/catalog-functions.service';
import { MessageService } from '../services/message.service';
import truncate from 'lodash.truncate';

@Component({
  selector: 'app-catalog-functions',
  templateUrl: './catalog-functions.component.html',
  styleUrls: ['./catalog-functions.component.scss']
})
export class CatalogFunctionsComponent implements OnInit {
  isLoading: boolean = true;
  isDataLoaded: boolean = false;
  data: any;
  defaultDescription: string = 'There is no description at this time.';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    // private service: CatalogService,
    private functionService: CatalogFunctionsService,
    private zone: NgZone,
    private messageService: MessageService,
    private renderer: Renderer2
  ) { }

  ngOnInit() {
    this.zone.run(() => {
      this.functionService.getFunctionsFromCatalogue({}).subscribe((catalogFunctions) => {
        this.isLoading = false;
        this.isDataLoaded = true;

        if (catalogFunctions[0] instanceof Array){
          this.data = catalogFunctions[0];
        } else {
          this.data = catalogFunctions;
        }

        // convert tags from string to string[]
        // this.handleDescriptionForEachFunction();
        this.handleTagsForEachFunction();
        this.messageService.sendSearchableFunctions(this.data);
      });
    });
  }

  // handleDescriptionForEachFunction() {
  //   this.data = this.data.map((item) => {
  //     // keep `item.description` clean
  //     if (!item.description) {
  //       item.updatedDescription = this.defaultDescription;
  //       item.showMoreOrLess = false;
  //       return item;
  //     }

  //     if (item.description && item.description.length >= 140) {
  //       item.updatedDescription = truncate(item.description, {
  //         length: 140, // maximum 140 characters
  //         separator: /,?\.* +/ // separate by spaces, including preceding commas and periods
  //       });
  //       item.showMoreOrLess = true;
  //       item.learnMore = true;
  //     }

  //     return item;
  //   });
  // }

  // showMore(event) {
  //   event.preventDefault();
  //   event.stopPropagation();

  //   const id = event.target.id;
  //   this.data = this.data.map((item) => {
  //     if (id === item.name) {
  //       item.updatedDescription = this.defaultDescription;
  //       item.learnMore = false;
  //     }
  //     return item;
  //   });
  // }

  // showLess(event) {
  //   event.preventDefault();
  //   event.stopPropagation();

  //   this.handleDescriptionForEachFunction();
  // }

  handleTagsForEachFunction() {
    console.log('data: ', typeof this.data, this.data);
    this.data.forEach((o) => {
      if (o.tags && o.tags.length > 0) {
        const spl = o.tags.split(',');
        o.tags = spl;
      }
    });
  }
}
