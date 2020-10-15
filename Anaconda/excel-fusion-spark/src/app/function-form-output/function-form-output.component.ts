import { Component, OnInit, Input } from '@angular/core';
import { MessageService } from '../services/message.service';
import { Subscription } from 'rxjs';
import { FunctionInputOutputService } from '../services/function-input-output.service';

/*
Example Responses:
{
  "stream": ["None\n"],
  "error": null,
  "result": "None\n",
  "display_data": {
    "text/plain": "<Figure size 504x504 with 1 Axes>",
    "image/png": "iVB...."
  }
}

or

{
  "display_data": null,
  "error": null,
  "result": {
    "Result": "Hello World"
  }
  stream: [
    {
      "Result": "Hello World"
    }
  ]
}
 */


@Component({
  selector: 'app-function-form-output',
  templateUrl: './function-form-output.component.html',
  styleUrls: ['./function-form-output.component.css']
})
export class FunctionFormOutputComponent implements OnInit {
  data: any;
  subscription: Subscription;
  isDataAvailable: boolean = false;
  displayMediaData: boolean = false; // see ['display_data']
  mediaImageSource: string = '';

  constructor(
    private fio: FunctionInputOutputService
  ) { }

  ngOnInit() {
      // this.subscription = this.fio
      //     .getOutputDataFromParent()
      //     .subscribe(
      //       (message) => {
      //         // CORS Issue: FunctionFormComponent $post subscription is firing twice
      //         // causing this subscription to fire twice;
      //         if (this.data) { return; }

      //         this.toggleIsDataAvailable();
      //         this.data = message;
      //         this.handleRendering();
      //       },
      //       (error) => {
      //         console.log('error while trying to get output on function', error);
      //       }
      //     );
  }

  toggleIsDataAvailable() {
    this.isDataAvailable = !this.isDataAvailable;
  }

  toggleDisplayMediaData() {
    this.displayMediaData = !this.displayMediaData;
  }

  handleRendering() {
    if (this.data && this.data['display_data'] && this.data['display_data']['image/png']) {
      this.handleImageRendering();
    }
  }

  handleImageRendering() {
    this.toggleDisplayMediaData();
    this.mediaImageSource = 'data:image/png;base64,' + this.data['display_data']['image/png'];
    console.log('asdadsg: ', this.data['display_data']['image/png'])
  }
}
