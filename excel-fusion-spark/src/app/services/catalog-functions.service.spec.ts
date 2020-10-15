import { TestBed } from '@angular/core/testing';

import { CatalogFunctionsService } from './catalog-functions.service';

describe('CatalogFunctionsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CatalogFunctionsService = TestBed.get(CatalogFunctionsService);
    expect(service).toBeTruthy();
  });
});
