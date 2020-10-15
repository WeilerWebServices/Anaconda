import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  // show = false;

  // toggleCollapse() {
  //   this.show = !this.show;
  // }

  // onClose() {
  //   this.show = false;
  // }

  constructor(
    private router: Router
  ) {

  }

  // For Fusion Spark Demo
  clickLogo() {
    this.router.navigate(['/']);
  }
  // END: For Fusion Spark Demo
}
