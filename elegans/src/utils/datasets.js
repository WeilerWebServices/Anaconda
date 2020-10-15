define([
    "utils/range",
    "utils/database"
],function(Range, DataBase){

    /*
     MatrixDataset:

     *** arguments ***
     data: [object] 3 nested array like ones generated by numpy.meshgrid.
     e.g. {
        x: [
           [1,2,3],
           [2,4,5],
        ],
        y: [
           [1,2,3],
           [2,4,5],
        ],
        z: [
           [1,2,3],
           [2,4,5],
        ],
     }

     *** properties ***
     ranges: the range of each column
     raw: given data
     */
    function MatrixDataset(data){
	var ranges = {};
	if(typeof data == "string"){
	    this.raw = DataBase.find(data);
	}else{
	    this.raw = data;
	}
	for(var i in data){
	    ranges[i] = new Range(
		d3.max(this.raw[i], function(d){return Math.max.apply(null,d);}),
		d3.min(this.raw[i], function(d){return Math.min.apply(null,d);})
	    );
	}
	this.ranges = ranges;
	this.raw = data;
	return this;
    }

    /*
     ArrayDataset: 
     *** arguments ***
     data: [object] 2 nested array
     e.g. {
        x: [1,2,3,4,...,10], // x
        y: [2,3,4,5,...,11], // y
        z: [3,4,5,6,...,12]  // z
     }

     *** properties ***
     ranges: the range of each column
     raw: given data
     */
    function ArrayDataset(data){
	this.ranges = {};
	if(typeof data == "string"){
	    this.raw = DataBase.find(data);
	}else{
	    this.raw = data;
	}
	for(var i in this.raw){
	    this.ranges[i] = new Range(
		d3.max(this.raw[i]),
		d3.min(this.raw[i])
	    );
	}
    }

    /*
     CompressedDataset: compressed data for volume rendering

     *** arguments ***
     data: [string] base64 encoded image
     e.g.
     'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAIAAAD/gAIDAAAANElEQVR4nO3BAQ0AAADCoPd
     PbQ43oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfgx1lAABqFDyOQAAAABJRU5ErkJggolQTkcNChoKAAAADUlIR
     FIAAABkAAAAZAgCAAAA/4ACAwAAADRJREFUeJztwQENAAAAwqD3T20ON6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
     AAH4MdZQAAahQ8jkAAAAASUVORK5CYII='

     *** properties ***
     ranges: the range of each column
     */
    function CompressedDataset(data){
	this.raw = data;
	this.ranges = {
	    x: [0, 1],
	    y: [0, 1],
	    z: [0, 1]
	};
	return this;
    }

    var Datasets = {
	Matrix:MatrixDataset,
	Array:ArrayDataset,
	Compressed: CompressedDataset
    };

    return Datasets;
});