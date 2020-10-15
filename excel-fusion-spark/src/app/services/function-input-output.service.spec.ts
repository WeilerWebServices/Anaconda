import { TestBed } from '@angular/core/testing';

import { FunctionInputOutputService } from './function-input-output.service';

describe('FunctionInputOutputService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: FunctionInputOutputService = TestBed.get(FunctionInputOutputService);
    expect(service).toBeTruthy();
  });
});
