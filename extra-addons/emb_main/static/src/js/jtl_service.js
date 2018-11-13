/**
 * Created by: shen fei 
 * Date: 2018/05/11
 * shenfei
 */
odoo.define('emb_main.StServiceList', function (require) {
    "use strict";

    var core = require('web.core');
    var form_common = require('web.form_common');

    var JtlService = form_common.AbstractField.extend({

        template: 'StServiceList',

        start: function () {
            var self = this;
            this._super();
            var refacted_data = this.refact_data();
            this.total_quantity = 0;
        },
        refact_data: function () {
            var self = this;
            var table_data = JSON.parse(this.get_value());
            self.total_quantity = 0;
            if (table_data && table_data.length > 0) {
                table_data.forEach(function (item) {
                    var request_quantity = JSON.parse(item['request_quantity']);
                    request_quantity.forEach(function (sub_item) {
                        var line_data = {};
                        // Product color
                        var pc = sub_item['color'];
                        var pc_tl = 'None';
                        if (pc != null && pc != undefined) {
                            pc_tl = '<span style="width: 30px;height:30px;background:' + pc + ';display:block;"></span>';
                        }
                        line_data['c3'] = pc_tl;
                        var product_sl = sub_item['size'];
                        var sum_count_node = product_sl.shift();
                        // If there are many colors
                        while (product_sl.length > 0) {
                            var node_tmp = product_sl.shift();
                            for (var key in node_tmp) {
                                if (key in sum_count_node) {
                                    sum_count_node[key] = sum_count_node[key] + node_tmp[key];
                                } else {
                                    sum_count_node[key] = node_tmp[key];
                                }
                            }
                        }
                        // Format: s:12 l:2 m:4
                        line_data['c7'] = self.translate_size_label(sum_count_node);
                        // Compute quantity
                        var broker_product_quantity = 0;
                        for (var key in sum_count_node) {
                            broker_product_quantity = broker_product_quantity + sum_count_node[key];
                            console.log(" Num" + self.total_quantity);
                        }
                        self.total_quantity = self.total_quantity + broker_product_quantity;
                        line_data['c9'] = broker_product_quantity;
                        // Product brand
                        line_data['c1'] = item['broker_product_brand'];
                        // Product uid
                        line_data['c2'] = item['broker_product_style'];
                        // Product package number here
                        line_data['c5'] = item['broker_product_package'];
                        // Product location in inventory shelf.
                        line_data['c6'] = item['broker_product_location'];
                        // Logo services UID
                        line_data['c11'] = item['logo_uids'];
                        // Product image
                        line_data['c4'] = item['broker_product_picture'];
                        // Order line description
                        line_data['c10'] = item['name'];
                        // Logo services List
                        line_data['c8'] = 'Embroidery';
                        self.make_render_line(line_data);
                    });
                });
                console.log(" Num" + self.total_quantity);
                self.render_total_quantity(self.total_quantity);
            }
        },
        translate_size_label: function (size_data) {
            var lbs = [];
            for (var key in size_data) {
                var lbs_key = key.toUpperCase() + ":" + size_data[key];
                lbs.push(lbs_key);
            }
            return lbs.join("<br />");
        },
        make_render_line: function (item) {
            var parent_node = this.getParent().$("#st_service_list").find('tbody');
            var tr = $("<tr>");
            var total_headers = 11;
            for (var k = 1; k <= total_headers; k++) {
                var key = 'c' + k;
                var td = $("<td>").append(item[key]);
                if (k == 1) {
                    td.attr("style", "width:15%");
                }
                tr.append(td);
            }
            parent_node.append(tr);
        },
        render_total_quantity: function (num) {
            var parent_node = this.getParent().$("#st_service_list").find('tbody');
            var tr = $("<tr>");
            var total_headers = 11;
            for (var k = 1; k <= total_headers; k++) {
                if (k == 9) {
                    var td = $("<td>").append('Total Qty:' + num);
                    tr.append(td);
                } else {
                    var td_emp = $("<td>").append(' ');
                    tr.append(td_emp);
                }
            }
            parent_node.append(tr);
        }
    });

    core.form_widget_registry.add('jtl_service', JtlService);

    return {
        JtlService: JtlService,
    };
});