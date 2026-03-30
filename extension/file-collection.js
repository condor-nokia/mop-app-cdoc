
const runCommand = require('./run-command.js')
const fs = require('fs');


module.exports.register = async function ({ config }) {
  this.on('contentAggregated', async ({ contentAggregate }) => {
    contentAggregate.forEach((content) => {
      const cloneFile = Object.assign({}, content.files[0])
      let tmpFiles = []
      fs.readdirSync(config.scanDir).filter((e) => e === content.version).forEach((version) => {
        const listFile = scanFileInDir(`${config.scanDir}/${version}`)
        listFile.forEach((path) => {
          const generatedFileContents = fs.readFileSync(path)
          const pathPattern = path.replace(`${config.scanDir}/${version}`, "pages") //extracts path
          const tmpFile = buildFile(cloneFile, config.pipelineName, generatedFileContents, pathPattern)
          tmpFiles.push(tmpFile)
        })
      })
      tmpFiles.forEach((file) => {
        content.files.push(file)
      })
    })
  })
}

function buildFile(file, module, contents, fileDir) {
  const filename = fileDir.substring(fileDir.lastIndexOf('/') + 1)
  const history = [`modules/${module}/${fileDir}`]
  const cwd = file._cwd
  const src = {
    abspath: `${cwd}/docs/modules/${module}/${fileDir}`,
    path: `modules/${module}/${fileDir}`,
    basename: filename,
    stem: filename.split(".")[0],
    extname: `.${filename.split(".")[1]}`,
    origin: file.src.origin,
    fileUri: `file:///${cwd}/docs/modules/${module}/${fileDir}`
  }

  const tmpFile = Object.assign(file, {
    contents: contents,
    src: src,
    history: history,
    path: `modules/${module}/${fileDir}`

  })
  Object.defineProperty(tmpFile, "title", {
    value: "",
    enumerable: true,
    configurable: true
  });

  return tmpFile
}

function scanFileInDir(dir) {
  let files = []
  const listFile = fs.readdirSync(dir, { withFileTypes: true })

  for (const item of listFile) {
    if (item.isDirectory()) {
      files = [...files, ...scanFileInDir(`${dir}/${item.name}`)];
    } else {
      files.push(`${dir}/${item.name}`);
    }
  }
  return files
}
