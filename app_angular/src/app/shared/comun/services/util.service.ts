import {Injectable} from "@angular/core";

@Injectable()
export class UtilService {


    existeItem(item, list) {
        return list.indexOf(item) > -1;
    }

    existeItemPorId(item, list) {
        for (let element of list) {
            if (element.id == item.id) {
                return true;
            }
        }
        return false;
    }

    seleccionarItem(item, list) {
        var idx = list.indexOf(item);
        if (idx > -1) {
            list.splice(idx, 1);
        } else {
            list.push(item);
        }
    }

}
