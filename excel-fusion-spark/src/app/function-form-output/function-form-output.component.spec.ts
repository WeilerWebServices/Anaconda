import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FunctionFormOutputComponent } from './function-form-output.component';

describe('FunctionFormOutputComponent', () => {
  let component: FunctionFormOutputComponent;
  let fixture: ComponentFixture<FunctionFormOutputComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FunctionFormOutputComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FunctionFormOutputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
