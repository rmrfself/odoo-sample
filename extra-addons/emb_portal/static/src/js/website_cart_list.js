odoo.define('emb_portal.website_logo_edit', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var website = require('website.website');
    var Model = require('web.Model');

    var qweb = core.qweb;
    var _t = core._t;
    var ZeroClipboard = window.ZeroClipboard;

    var exports = {};
    /**
     * Author: Shenfei
     * 创建左侧类型Bar
     */
    var CartListView = Widget.extend({
        /**
         * 初始函数
         */
        init: function () {
            this._super();
        },
        start: function () {
            this.loadCartView();
            $('.datepicker').datepicker();
        },
        loadCartView: function () {
            var self = this;
            ajax.jsonRpc('/portal/load_cart_list', 'call', {})
                .then(function (result) {
                    console.log(result);
                    var sale_order_lines = result;
                    if (sale_order_lines.length > 0) {
                        $("#form-info-body").show();
                        self.setCartViewList(sale_order_lines);
                    } else {
                        $("#form-info-body").hide();
                        $("#cart-list-table").html("<tr><td colspan='15'>No data found in your cart.</td></tr>")
                    }

                })
                .fail(function () {
                    var message = _t("Unable to get recent links");
                    self.$el.append("<div class='alert alert-danger'>" + message + "</div>");
                });
        },
        setCartViewList: function (list) {
            list.map(function (item) {
                var trEle = $("<tr>");
                trEle.append($("<td>").append("<input type='checkbox' id='cart_select_' " + item.id + " />"));
                var imgBaseSrc = "/website/image/sale.order.line/" + item.id + "/image_variant/";
                var imgSrc = imgBaseSrc + "60x60";
                trEle.append($("<td>").append("<a href=“#” id=cart-img-" + item.id + "><img src='" + imgSrc + "' /></a>"));
                trEle.append($("<td>").append("<span>Dst File</span>"));
                trEle.append($("<td>").append("<span>T-Shirt</span>"));
                trEle.append($("<td>").append("<span>Center</span>"));
                trEle.append($("<td>").append("<span>" + (item.product_color || '') + "</span>"));
                trEle.append($("<td>").append("<span>" + item.service_surcharge_ids + "</span>"));
                trEle.append($("<td>").append("<input type='text' value='" + (JSON.parse(item.product_sbu)['s'] || 0) + "' style='width:50px;' />"));
                trEle.append($("<td>").append("<input type='text' value='" + (JSON.parse(item.product_sbu)['m'] || 0) + "' style='width:50px;' />"));
                trEle.append($("<td>").append("<input type='text' value='" + (JSON.parse(item.product_sbu)['l'] || 0) + "' style='width:50px;' />"));
                trEle.append($("<td>").append("<input type='text' value='" + (JSON.parse(item.product_sbu)['xl'] || 0) + "' style='width:50px;' />"));
                trEle.append($("<td>").append("<input type='text' value='" + (item.price_unit || 0) + "' style='width:50px;' />"));
                trEle.append($("<td>").append("<input type='text' value='" + item.discount + "' style='width:50px;' />"));
                trEle.append($("<td colspan='2'>").append('<select data-id="' + item.id + '" title="Actions" class="selectpicker show-menu-arrow"><option value="edit">Edit</option><option value="update">Update</option><option value="delete">Delete</option></select>'));
                $("#cart-list-table").append(trEle);
                $("#cart-img-" + item.id).hover(function(){
                    $(this).find(".demo-img").remove();
                    var bigImageSrc = imgBaseSrc + "/200x200";
                    var imgNode = "<span class='demo-img' style='position:absolute;left:260px;top:100px;z-index:999;'><img src='" +  bigImageSrc + "' /></span>";
                    $(this).append(imgNode);
                    return false;
                },function(){
                    $(this).find(".demo-img").remove();
                });
                return item;
            });
            $('.selectpicker').selectpicker({
                width: 'fit'
            });
            $('.selectpicker').on('changed.bs.select', function (e) {
                var action = $(this).val();
                var itemId = $(this).attr("data-id");
                switch (action) {
                    case 'edit':
                        bootbox.confirm({
                            title: "Edit",
                            message: "This action will override current settings. Continue?",
                            buttons: {
                                confirm: {
                                    label: '<i class="fa fa-check"></i> Yes',
                                    className: 'btn-success'
                                },
                                cancel: {
                                    label: '<i class="fa fa-times"></i> No',
                                    className: 'btn-default'
                                }
                            },
                            callback: function (result) {
                                if (result) {
                                    window.location.href = '/portal/index/?cart_id=' + itemId;
                                }
                            }
                        });
                        break;
                    case 'update':
                        bootbox.confirm({
                            title: "Update",
                            message: "Do you want to update current settings?",
                            buttons: {
                                confirm: {
                                    label: '<i class="fa fa-check"></i> Yes',
                                    className: 'btn-success'
                                },
                                cancel: {
                                    label: '<i class="fa fa-times"></i> No',
                                    className: 'btn-default'
                                }
                            },
                            callback: function (result) {
                                if (result) {

                                }
                            }
                        });
                        break;
                    case 'delete':
                        bootbox.confirm({
                            title: "Delete",
                            message: "Do you want to delete current item?",
                            buttons: {
                                confirm: {
                                    label: '<i class="fa fa-check"></i> Yes',
                                    className: 'btn-success'
                                },
                                cancel: {
                                    label: '<i class="fa fa-times"></i> No',
                                    className: 'btn-default'
                                }
                            },
                            callback: function (result) {
                                if (result) {
                                    ajax.jsonRpc("/portal/remove_sale_line", 'call', {
                                        id: itemId
                                    }).then(function (apiResult) {
                                        if (apiResult.error) {
                                            $.growlUI('Failure', apiResult);
                                        } else {
                                            $.growlUI('Success', 'Item is removed already.');
                                            location.reload();
                                        }
                                    });

                                }
                            }
                        });
                        break;
                }
            });
        }
    })

    /**
     * 等待页面加载完成后，加载数据
     */
    base.ready().done(function () {
        var cartView = new CartListView();
        cartView.start();
    });
});