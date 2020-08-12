# covid19-nepal

This software performs simulations of covid19 spread in Nepal. For more details, please have a look at: [About Intercity Model](./about.md)

## How to deploy

### Database Used

- "intercity_dashboard": [Document Structure](./intercity_dashboard.json)
    The frontend adds the document into this database the the aforementioned format. While adding the document, the "_id" parameter is genereted by the CouchDB. It provides the unique id for corresponding result of intercity_results.

- "intercity_results": [Document Structure](./intercity_results.json)
    After the model has carried out the simulation, this database is updated with the "_id" key.  
