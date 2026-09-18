class MysqlFunctions:

    def __init__(self, ctx):
        self.ctx = ctx

    def exec_mysql(self, dbConnection_in, side, market1, market2, market3, price1, price2, price3, amount1_in, amount1_out, perc1, amount2_in, amount2_out, perc2, _date_creation):
        try:
            sqlInsert = 'INSERT INTO `opportunities` (`side`, `market1`, `market2`, `market3`, `price1`, `price2`, `price3`, `amount1_in`, `amount1_out`, `perc1`, `amount2_in`, `amount2_out`, `perc2`, `date_creation`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            mySQLCursor = dbConnection_in.cursor()
            mySQLCursor.execute(sqlInsert, (side, market1, market2, market3, price1, price2, price3, amount1_in, amount1_out, perc1, amount2_in, amount2_out, perc2, _date_creation))
            mySQLCursor.close()
            dbConnection_in.close()
        except Exception as e:
            print('Exception: %s' % e)
        return

    def exec_lockunlock(self, dbConnection_in, _data, _date_creation):
        try:
            sqlInsert = 'INSERT INTO `lockunlock` (`script`, `data`, `date_creation`) VALUES (%s, %s, %s)'
            mySQLCursor = dbConnection_in.cursor()
            mySQLCursor.execute(sqlInsert, ('stop', _data, _date_creation))
            mySQLCursor.close()
            dbConnection_in.close()
        except Exception as e:
            print('Exception: %s' % e)
        return

    def exec_orders(self, dbConnection_in, _data, _date_creation):
        try:
            sqlInsert = 'INSERT INTO `binance_orders` (`script`, `data`, `date_creation`) VALUES (%s, %s, %s)'
            mySQLCursor = dbConnection_in.cursor()
            mySQLCursor.execute(sqlInsert, ('stop', _data, _date_creation))
            mySQLCursor.close()
            dbConnection_in.close()
            self.ctx.desliga = True
            self.ctx.waiting = False
        except Exception as e:
            print('Exception: %s' % e)
        return

    def exec_log(self, dbConnection_in, _data, _date_creation):
        try:
            sqlInsert = 'INSERT INTO `log` (`robot`, `version`, `data`, `date_creation`) VALUES (%s, %s, %s, %s)'
            mySQLCursor = dbConnection_in.cursor()
            mySQLCursor.execute(sqlInsert, (1, 'bot_slave10', _data, _date_creation))
            mySQLCursor.close()
            dbConnection_in.close()
        except Exception as e:
            print('Exception: %s' % e)
        return

