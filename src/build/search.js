class AsyncSearchResultsFetcher {
    constructor(endpoint, callback) {
        this.endpoint = endpoint;
        this.results_ready_callback = callback;

        this.remote_query = null;
        this.remote_results = [];
        this.request_in_flight = false;
        this.remote_query_timout = 500;
    }

    async updateRemoteQuery() {
        if (this.request_in_flight) {
            return;
        }

        let request_query = this.query;
        this.request_in_flight = true;
        let res = await $.ajax(this.endpoint + "?q=" + request_query);

        this.remote_query = request_query;
        this.remote_results = res;

        this.remoteResultsReady()

        // Wait the timout time before allowing another remote query
        setTimeout(() => {
            this.request_in_flight = false;

            // If the local query was updated while performing the remote query, start another remote query
            if (this.remote_query !== this.query) {
                this.updateRemoteQuery().then();
            }
        }, this.remote_query_timout);
    }

    updateQuery(q) {
        if (q === this.query) { return; }
        this.query = q;
        this.updateRemoteQuery().then();
        this.performLocalSearch(q)
    }

    remoteResultsReady() {
        this.performLocalSearch();
    }

    performLocalSearch() {
        // Don't search locally, since results are going into a datalist. The browser will handle this on its own
        /*let results = this.remote_results.filter((processor) => {
            return processor["model"].toLocaleLowerCase().includes(this.query.toLocaleLowerCase());
        });

        this.results_ready_callback(results);*/
        this.results_ready_callback(this.remote_results);
    }
}

let PROCESSOR_SEARCH = new AsyncSearchResultsFetcher("/build/processor/search", onProcessorResults);

export function onProcessorSearchKeyup(event) {
    PROCESSOR_SEARCH.updateQuery(event.target.value);
}

function onProcessorResults(results) {
    $("#processor-results > option").remove();

    for (var i = 0; i < results.length; i++) {
        let item = results[i]["model"];
        $("#processor-results").append(new Option(item, item));
    }
}

let GRAPHICS_SEARCH = new AsyncSearchResultsFetcher("/build/graphics/search", onGraphicsResults)

export function onGraphicsSearchKeyup(event) {
    GRAPHICS_SEARCH.updateQuery(event.target.value);
}

function onGraphicsResults(results) {
    $("#graphics-results > option").remove();

    for (var i = 0; i < results.length; i++) {
        let item = results[i]["model"];
        $("#graphics-results").append(new Option(item, item));
    }
}