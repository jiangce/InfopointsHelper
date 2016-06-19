# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
from ui.uiMainWindow import Ui_MainWindow
from pointtable import *
import sys
import os


getOpenFileName = QtWidgets.QFileDialog.getOpenFileName
getSaveFileName = QtWidgets.QFileDialog.getSaveFileName
warning = QtWidgets.QMessageBox.warning
information = QtWidgets.QMessageBox.information


class Main_Windows(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self._source_points = []
        self._filter_souce_points = []
        self.setupUi(self)
        # self.showMaximized()
        self.button_load_t.clicked.connect(self._load_target)
        self.button_load_s.clicked.connect(self._load_source)
        self.table_t.itemSelectionChanged.connect(self._filter)
        self.edit_include.textChanged.connect(self._filter)
        self.edit_outclude.textChanged.connect(self._filter)
        self.button_fill.clicked.connect(self._fill_point)
        self.cb_showall.stateChanged.connect(self._filter)
        self.button_next.clicked.connect(self._to_next)
        self.button_reset_num.clicked.connect(self._reset_num)
        self.button_save.clicked.connect(self._target_save)
        self.button_opensave.clicked.connect(self._load_save)
        self.edit_target_name_location.textChanged.connect(self._t_name_location)
        self.edit_target_name_location_non.textChanged.connect(self._t_name_location)
        self.edit_target_num_location.textChanged.connect(self._t_num_location)
        self.button_output_right.clicked.connect(self._output_right)

    def _load_target(self):
        filename = getOpenFileName(self, '请打开目标点表文件', '',
                                   '文本文件(*.txt);;All File(*.*)')[0]
        if filename:
            os.chdir(os.path.dirname(filename))
            try:
                self._set_table_target(loadTargetPoints(filename))
                information(self, '提示', '文件解析成功！')
            except:
                warning(self, '错误', '选择的文件无法解析！')

    def _load_save(self):
        filename = getOpenFileName(self, '请打开输出的文件', '',
                                   '文本文件(*.txt);;All File(*.*)')[0]
        if filename:
            os.chdir(os.path.dirname(filename))
            try:
                with open(filename) as f:
                    txt = f.read()
                lines = [line.strip() for line in txt.split('\n') if line.strip()]
                target_points = []
                for line in lines:
                    p = line.split()
                    print(p)
                    target_points.append((' '.join(p[1:]), int(p[0])))
                self._set_table_target(target_points)
                information(self, '提示', '文件解析成功！')
            except:
                raise
                warning(self, '错误', '选择的文件无法解析！')

    def _set_table_target(self, tps):
        self.table_t.setRowCount(len(tps))
        for i in range(len(tps)):
            name, p = tps[i]
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table_t.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(p))
            item.setTextAlignment(0x4 | 0x80)
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table_t.setItem(i, 1, item)
            self.table_t.resizeColumnsToContents()
        self._t_name_location()
        self._t_num_location()

    def _get_points_from_target_table(self):
        points = []
        for i in range(self.table_t.rowCount()):
            name, point = self.table_t.item(i, 0).text(), \
                          int(self.table_t.item(i, 1).text())
            points.append((name, point))
        return points

    def _load_source(self):
        filename = getOpenFileName(self, '请打开源点表文件', '',
                                   'Excel文件(*.xls;*.xlsx);;All File(*.*)')[0]
        if filename:
            os.chdir(os.path.dirname(filename))
            try:
                self._source_points = loadSourcePoints(filename)
                self._filter()
                information(self, '提示', '文件解析成功！')
            except Exception as e:
                warning(self, '错误', str(e))

    def _set_table_source(self):
        if not self.cb_showall.isChecked():
            sps = self._filter_souce_points
        else:
            target_point_number_set = set(
                [p[1] for p in self._get_points_from_target_table() if
                 p[1] >= 0])
            source_point_number_set = set(
                [p[1] for p in self._filter_souce_points if p[1] >= 0])
            delta_point_number_ser = source_point_number_set - target_point_number_set
            sps = [point for point in self._filter_souce_points if
                   point[1] in delta_point_number_ser]
        selected_items = self.table_t.selectedItems()
        sentence = None
        if selected_items:
            item = selected_items[0]
            sentence = item.text()
        sps = getOrderSource(sentence, sps)
        self.table_s.setRowCount(len(sps))
        for i in range(len(sps)):
            name, p = sps[i]
            item = QtWidgets.QTableWidgetItem(str(p))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            item.setTextAlignment(0x4 | 0x80)
            self.table_s.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table_s.setItem(i, 1, item)
            self.table_s.resizeColumnsToContents()

    def _filter(self):
        self._filter_souce_points = filterSource(self.edit_include.text(),
            self.edit_outclude.text(),
            self._source_points)
        self._set_table_source()
        self._t_num_location()

    def _fill_point(self):
        selected_items = self.table_t.selectedItems()
        if not selected_items:
            return
        targetitem = selected_items[1]
        selected_items = self.table_s.selectedItems()
        sourceitem = None
        if selected_items:
            sourceitem = selected_items[0]
        elif self.table_s.rowCount() == 1:
            sourceitem = self.table_s.item(0, 0)
        if sourceitem:
            ts = set()
            for i in range(self.table_t.rowCount()):
                num = self.table_t.item(i, 1).text()
                if int(num) >= 0:
                    ts.add(num)
            if sourceitem.text() in ts:
                warning(self, '错误', '该点号已经使用过！')
                return
            targetitem.setText(sourceitem.text())
            if self.cb_auto_next.isChecked():
                self._to_next()

    def _to_next(self):
        selectedindexes = self.table_t.selectedIndexes()
        row = 0
        if selectedindexes:
            row = selectedindexes[0].row()
        row += 1
        while row < self.table_t.rowCount():
            if int(self.table_t.item(row, 1).text()) < 0:
                break
            row += 1
        if row < self.table_t.rowCount():
            self.table_t.selectRow(row)

    def _reset_num(self):
        selected = self.table_t.selectedItems()
        if selected:
            item = selected[1]
            item.setText('-1')
            self._filter()

    def _get_target_points(self):
        result = []
        for row in range(self.table_t.rowCount()):
            result.append((self.table_t.item(row, 0).text(),
                           int(self.table_t.item(row, 1).text())))
        return result

    def _target_save(self):
        filename = getSaveFileName(self, '请指定保存文件', '', '文本文件(*.txt)')[0]
        if filename:
            os.chdir(os.path.dirname(filename))
            lines = []
            for row in range(self.table_t.rowCount()):
                line = '%s\t%s' % (
                    self.table_t.item(row, 1).text(),
                    self.table_t.item(row, 0).text())
                lines.append(line)
            if lines:
                with open(filename, 'w') as f:
                    f.write('\n'.join(lines))
                information(self, '提示', '文件保存成功！')

    def _t_name_location(self):
        condition1 = self.edit_target_name_location.text().strip()
        condition2 = self.edit_target_name_location_non.text().strip()
        pset = set()
        if condition1 or condition2:
            points = filterSource(condition1, condition2,
                                  self._get_target_points())
            pset = set(points)
        for row in range(self.table_t.rowCount()):
            item = self.table_t.item(row, 0)
            num = int(self.table_t.item(row, 1).text())
            if (item.text(), num) in pset:
                item.setBackground(QtGui.QColor.fromRgb(120, 120, 255))
            else:
                item.setBackground(QtGui.QColor.fromRgb(255, 255, 255))

    def _t_num_location(self):
        condition = self.edit_target_num_location.text()
        for row in range(self.table_t.rowCount()):
            item = self.table_t.item(row, 1)
            num = item.text()
            if num == condition:
                item.setBackground(QtGui.QColor.fromRgb(255, 120, 120))
            else:
                item.setBackground(QtGui.QColor.fromRgb(255, 255, 255))

    def _output_right(self):
        filename = getSaveFileName(self, '请指定导出文件', '', '文本文件(*.txt)')[0]
        if filename:
            os.chdir(os.path.dirname(filename))
            result = []
            for row in range(self.table_s.rowCount()):
                num = self.table_s.item(row, 0).text()
                name = self.table_s.item(row, 1).text()
                result.append('\t'.join([num, name]))
            with open(filename, 'w') as f:
                f.write('\n'.join(result))

    def closeEvent(self, e):
        if QtWidgets.QMessageBox.question(self, '提示', '确定要退出程序？',
                                          QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel) \
                == QtWidgets.QMessageBox.Cancel:
            e.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = Main_Windows()
    mw.show()
    sys.exit(app.exec_())
