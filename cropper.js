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
            }
            else if (filter == undefined) {
                fileData.push(filename)
            };
        };
        resolve(fileData)
    });
};

function resize(file, val) {
    var mainImage = new Jimp(900, 700, 0xffffffff, function (err, image) {
        
    });
    console.log(path.resolve(__dirname, val))
    Jimp.read(path.resolve(__dirname, val), (err, img) => {
        if (err)
            console.error(err);
        else {
            /*var sz = r.annotation.size
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
            img.crop(x1, y1, x2, y2)*/
            if (img.bitmap.width > 900 || img.bitmap.height > 700) {
                var byWidth = img.bitmap.width > img.bitmap.height
                if (byWidth) {
                    img.resize(900, Jimp.AUTO)
                    mainImage.blit(img, 0, 350-(img.bitmap.height/2))
                        .write(pathDir + '/' + path.basename(val).split('.')[0] + '.jpg');
                }
                else {
                    img.resize(Jimp.AUTO, 700)
                    mainImage.blit(img, 450-(img.bitmap.width/2), 0)
                        .write(pathDir + '/' + path.basename(val).split('.')[0] + '.jpg');
                }
            }
            else {
                mainImage.blit(img, 450-(img.bitmap.width/2), 350-(img.bitmap.height/2))
                    .write(pathDir + '/' + path.basename(val).split('.')[0] + '.jpg');
            }
            /*mainImage.blit(img, 0, 0)
                .write(pathDira + '/a' + path.basename(val).split('.')[0] + '.jpg'); // save*/
        }
    })
}

var pathDir = './data/images/test/'

fromDir(pathDir).then((data) => {
    for (var i = 0; i < data.length; i++) {
        var val = data[i]
        resize(val, val)
    }
}).catch(console.log)