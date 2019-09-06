import {Injectable, Input} from "@angular/core";

@Injectable()
export class ConfigService {

    public searchEnabled = true;
    public orderEnabled = true;
    public globalSearchEnabled = true;
    public footerEnabled = false;
    public paginationEnabled = true;
    public exportEnabled = true;
    public editEnabled = false;

    @Input() rows: number;

    constructor() {
    }

}