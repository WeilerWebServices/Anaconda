import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CatalogFunctionsComponent } from './catalog-functions.component';

describe('CatalogFunctionsComponent', () => {
  let component: CatalogFunctionsComponent;
  let fixture: ComponentFixture<CatalogFunctionsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CatalogFunctionsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CatalogFunctionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
