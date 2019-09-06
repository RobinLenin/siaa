import { Pipe } from "@angular/core";

@Pipe({
    name: 'buscar',
    pure: false
})

export class BuscarPipe {

    constructor() {}

    transform(dataArr, filter) {
        if (typeof dataArr === "undefined") {
            return;
        }
        if (typeof filter === 'undefined' || Object.keys(filter).length === 0 || filter === "") {
            return dataArr;
        }
        filter = filter.toLocaleLowerCase()
        let data = [];
        dataArr.forEach((row) => {
            for (var value in row) {
                if (row.hasOwnProperty(value)) {
                    let element;
                    if (typeof row[value] === "object") {
                        element = JSON.stringify(row[value]);
                    }
                    if (typeof row[value] === "boolean") {
                        element = "" + row[value];
                    }
                    if (typeof row[value] === "string") {
                        element = row[value].toLocaleLowerCase();
                    }
                    if (typeof row[value] === "number") {
                        element = "" + row[value];
                    }

                    if (element.indexOf(filter) >= 0) {
                        data.push(row);
                        return;
                    }
                    if (element.indexOf(filter["value"]) >= 0) {
                        data.push(row);
                        return;
                    }
                }
            }
        });
        return data;
    }
}