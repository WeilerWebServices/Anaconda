import { TestBed } from '@angular/core/testing';

import { FusionSparkService } from './fusion-spark.service';

describe('FusionSparkService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: FusionSparkService = TestBed.get(FusionSparkService);
    expect(service).toBeTruthy();
  });
});
