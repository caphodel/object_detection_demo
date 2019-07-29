var convert = require('xml-js');
var fs = require('fs'), path = require('path')
var Jimp = require('jimp');

async function fromDir(startPath, filter) {
    return new Promise((resolve, reject) => {

        //console.log('Starting from dir '+startPath+'/');

        if (!fs.existsSync(startPath)) {
            console.log("no dir ", startPath);
            reject("no dir ", startPath)
            return;
        }

        var fileData = []

        var files = fs.readdirSync(startPath);
        for (var i = 0; i < files.length; i++) {
            var filename = path.join(startPath, files[i]);
            var stat = fs.lstatSync(filename);
            if (stat.isDirectory()) {
                fromDir(filename, filter); //recurse
            }
            else if (filename.indexOf(filter) >= 0) {
                fileData.push(filename)
            };
        };
        resolve(fileData)
    });
};

function resize(xml, val) {
    var r = JSON.parse(convert.xml2json(xml, { compact: true, spaces: 4 }))
    var mainImage = new Jimp(900, 700, function (err, image) {
        
    });
    Jimp.read(r.annotation.path._text, (err, img) => {
        if (err)
            console.error(err);
        else {
            var sz = r.annotation.size
            var bb = r.annotation.object.bndbox
            var x1 = parseInt(bb.xmin._text) - 20
            var y1 = parseInt(bb.ymin._text) - 20
            var x2 = parseInt(bb.xmax._text) + 40 - x1
            var y2 = parseInt(bb.ymax._text) + 40 - y1
            if (x1 < 0)
                x1 = 0
            if (y1 < 0)
                y1 = 0
            if (x2 > parseInt(sz.width))
                x2 = sz.width
            if (y2 > parseInt(sz.height))
                y2 = sz.height
            img.crop(x1, y1, x2, y2)
            mainImage.blit(img, 0, 0)
                .write('./data/images/test/a' + path.basename(val).split('.')[0] + '.jpg'); // save
        }
    })
}

fromDir('./data/images/test', '.xml').then((data) => {
    for (var i = 0; i < data.length; i++) {
        var val = data[i]
        var xml = fs.readFileSync(path.resolve(__dirname, val), 'utf-8')
        resize(xml, val)
    }
}).catch(console.log)