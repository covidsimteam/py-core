/** 
 * This file will only be needed if you have an updated Gapanapas and Wards geojson files.
 * Use this to split your Wards and Gapanapas geojsons according to Provinces.
 * To run this file run npm install and then run node province-wise.split.js
*/

const fetch = require("node-fetch");
const fs = require('fs');

// change this to fit your geojson endpoint
function uriBuilder(type) {
  return `http://localhost:8081/shapefiles/nepal-map-governance/geojson/${type}_geo.json`;
}

async function getJson(path) {
  const response =  await fetch(path);
  return response.json();
}

function writeJson(filename, content) {
  fs.writeFile(`${filename}.json`, content, error => {
    if (error) {
      console.error(error);
      return;
    }
    console.log(`Wrote file: ${filename}`);
  })
}

const geoJsonTemplate = {
  _id: "",
  type: "FeatureCollection",
  features: []
}

async function provinceWiseSplitter(type) {
  const doc = await getJson(uriBuilder(type));
  const lCaseType = type.toLowerCase();
  if (doc._id === `gov_${lCaseType}`
      && doc.type === "FeatureCollection"
      && doc.features
      && doc.features.length) {
    [...Array(7).keys()].forEach(key => {
      const provinceNumber = key + 1;
      console.log(`Current Province: ${provinceNumber} for ${type}`);
      geoJsonTemplate._id = `${lCaseType}_province_${provinceNumber}`;
      geoJsonTemplate.features = [];
      geoJsonTemplate.features.push(
        doc.features.filter(feature => feature 
                            && feature.properties 
                            && (feature.properties.STATE_CODE === provinceNumber 
                              || feature.properties.PROVINCE === provinceNumber
                              )
                            ));
      writeJson(geoJsonTemplate._id, JSON.stringify(geoJsonTemplate));
    })
  }

}

async function run() {
  provinceWiseSplitter("Gapanapas");
  provinceWiseSplitter("Wards");
}

run();



// neo4j cypher test
// WITH 'http://localhost:8081/shapefiles/nepal_data/geojson/Highways_geo.json' AS uri
// CALL apoc.load.json(uri, null, null)
// YIELD value

// CREATE (highway:Highway {id: value._id})
// SET 
// highway.type = value.type,
// highway.features = value.features