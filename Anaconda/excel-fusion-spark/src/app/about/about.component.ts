import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {

  private extension;

  constructor() { }

  ngOnInit() {
    this.extension = this.getExtension();
  }

  getExtension(): string {
    if (Office.context.host === Office.HostType.Word) {
      return '.docx';
    } else if (Office.context.host === Office.HostType.Excel) {
      return '.xlsx';
    } else if (Office.context.host === Office.HostType.PowerPoint) {
      return '.pptx';
    } else {
      return null;
    }
  }
}
