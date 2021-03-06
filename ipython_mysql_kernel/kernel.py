#!/usr/bin/env python

import json
import os
import re
import signal

from IPython.kernel.zmq.kernelbase import Kernel
import pexpect

# keywords for completion
WORDS_LIST = [\
"ABS",
"ACOS",
"ADDDATE",
"ADDTIME",
"AES_DECRYPT",
"AES_ENCRYPT",
"ALTER",
"AND",
"AS",
"ASCII",
"ASIN",
"ATAN",
"ATAN2",
"AVG",
"AREA",
"ASBINARY",
"ASTEXT",
"BEGIN",
"BENCHMARK",
"BETWEEN",
"BIN",
"BINARY",
"BIT_AND",
"BIT_COUNT",
"BIT_LENGTH",
"BIT_OR",
"BIT_XOR",
"CASE",
"CAST",
"CEIL",
"CEILING",
"CHAR",
"CHARACTER_LENGTH",
"CHARSET",
"CHAR_LENGTH",
"COALESCE",
"COERCIBILITY",
"COLLATION",
"COMMIT",
"COMPRESS",
"CONCAT",
"CONCAT_WS",
"CONNECTION_ID",
"CONV",
"CONVERT",
"CONVERT_TZ",
"COS",
"COT",
"COUNT",
"CRC32",
"CREATE",
"CURDATE",
"CURRENT_DATE",
"CURRENT_TIME",
"CURRENT_TIMESTAMP",
"CURRENT_USER",
"CURTIME",
"CENTROID",
"CONTAINS",
"CROSSES",
"DATABASE",
"DATE",
"DATEDIFF",
"DATE_ADD",
"DATE_FORMAT",
"DATE_SUB",
"DAY",
"DAYNAME",
"DAYOFMONTH",
"DAYOFWEEK",
"DAYOFYEAR",
"DECODE",
"DEFAULT",
"DEGREES",
"DELETE",
"DES_DECRYPT",
"DES_ENCRYPT",
"DISTINCT",
"DIV",
"DROP",
"DIMENSION",
"DISJOINT",
"ELT",
"ENCODE",
"ENCRYPT",
"EXP",
"EXPORT_SET",
"EXTRACT",
"ENDPOINT",
"ENVELOPE",
"EQUALS",
"EXTERIORRING",
"FIELD",
"FIND_IN_SET",
"FLOOR",
"FORMAT",
"FOUND_ROWS",
"FROM",
"FROM_DAYS",
"FROM_UNIXTIME",
"GET_FORMAT",
"GET_LOCK",
"GLENGTH",
"GRANT",
"GREATEST",
"GROUP",
"GROUP_CONCAT",
"GEOMCOLLFROMTEXT",
"GEOMCOLLFROMWKB",
"GEOMFROMTEXT",
"GEOMFROMWKB",
"GEOMETRYCOLLECTION",
"GEOMETRYN",
"GEOMETRYTYPE",
"HAVING",
"HEX",
"HOUR",
"IF",
"IFNULL",
"IN",
"INET_ATON",
"INET_NTOA",
"INNER",
"INSERT",
"INSTR",
"INTERVAL",
"ISNULL",
"IS_FREE_LOCK",
"INTERIORRINGN",
"INTERSECTS",
"ISCLOSED",
"ISEMPTY",
"ISSIMPLE",
"JOIN",
"LAST_DAY",
"LAST_INSERT_ID",
"LCASE",
"LEAST",
"LEFT",
"LENGTH",
"LIKE",
"LIMIT",
"LN",
"LOAD_FILE",
"LOCALTIME",
"LOCALTIMESTAMP",
"LOCATE",
"LOG",
"LOG10",
"LOG2",
"LOWER",
"LPAD",
"LTRIM",
"LINEFROMTEXT",
"LINEFROMWKB",
"LINESTRING",
"MAKEDATE",
"MAKETIME",
"MAKE_SET",
"MASTER_POS_WAIT",
"MATCH",
"MAX",
"MBRCONTAINS",
"MBRDISJOINT",
"MBREQUAL",
"MBRINTERSECTS",
"MBROVERLAPS",
"MBRTOUCHES",
"MBRWITHIN",
"MD5",
"MICROSECOND",
"MID",
"MIN",
"MINUTE",
"MLINEFROMTEXT",
"MLINEFROMWKB",
"MOD",
"MONTH",
"MONTHNAME",
"MPOINTFROMTEXT",
"MPOINTFROMWKB",
"MPOLYFROMTEXT",
"MPOLYFROMWKB",
"MULTILINESTRING",
"MULTIPOINT",
"MULTIPOLYGON",
"NAME_CONST",
"NOW",
"NULLIF",
"NUMGEOMETRIES",
"NUMINTERIORRINGS",
"NUMPOINTS",
"OCT",
"OCTET_LENGTH",
"OLD_PASSWORD",
"ORD",
"ORDER",
"OVERLAPS",
"PASSWORD",
"PERIOD_ADD",
"PERIOD_DIFF",
"PI",
"POSITION",
"POW",
"POWER",
"PROCEDURE ANALYSE",
"POINT",
"POINTFROMTEXT",
"POINTFROMWKB",
"POINTN",
"POLYFROMTEXT",
"POLYFROMWKB",
"POLYGON",
"QUARTER",
"QUOTE",
"RADIANS",
"RAND",
"REGEXP",
"RELEASE_LOCK",
"RENAME",
"REPEAT",
"REPLACE",
"REVERSE",
"REVOKE",
"RIGHT",
"RLIKE",
"ROLLBACK",
"ROUND",
"ROW_COUNT",
"RPAD",
"RTRIM",
"SCHEMA",
"SECOND",
"SEC_TO_TIME",
"SELECT",
"SESSION_USER",
"SHA1",
"SHOW",
"SIGN",
"SIN",
"SLEEP",
"SOUNDEX",
"SOUNDS",
"SPACE",
"SQRT",
"SRID",
"STD",
"STDDEV",
"STDDEV_POP",
"STDDEV_SAMP",
"STRCMP",
"STR_TO_DATE",
"SUBDATE",
"SUBSTR",
"SUBSTRING",
"SUBSTRING_INDEX",
"SUBTIME",
"SUM",
"SYSDATE",
"SYSTEM_USER",
"STARTPOINT",
"TAN",
"TIME",
"TIMEDIFF",
"TIMESTAMP",
"TIMESTAMPADD",
"TIMESTAMPDIFF",
"TIME_FORMAT",
"TIME_TO_SEC",
"TO_DAYS",
"TRIM",
"TRUNCATE",
"TOUCHES",
"UCASE",
"UNCOMPRESS",
"UNCOMPRESSED_LENGTH",
"UNHEX",
"UNIQUE",
"UNIX_TIMESTAMP",
"UPDATE",
"UPPER",
"USER",
"UTC_DATE",
"UTC_TIME",
"UTC_TIMESTAMP",
"UUID",
"VALUES",
"VARIANCE",
"VAR_POP",
"VAR_SAMP",
"VERSION",
"WEEK",
"WEEKDAY",
"WEEKOFYEAR",
"WHERE",
"WITHIN",
"XOR",
"YEAR",
"YEARWEEK",
]

class MySQLKernel(Kernel):
    """MySQLKernel for IPython
       this program use pexpect to interact with the mysql process
       mysql configs are read from ~/.ipython/mysql_config.json
       default configs are
            mysql_config = {
               "user"     : "root",
               "host"     : "127.0.0.1",
               "port"     : "3306",
               "charset"  : "utf8"
            }
        you can set "password" in mysql_config.json if needed
    """
    implementation = 'MySQL'
    implementation_version = '0.1'
    language = 'mysql'
    language_version = '0.1'
    language_info = {
            'mimetype': 'text/plain',
            'name': 'mysql',
            'file_extension': '.sql',
            }
    banner = "MySQL kernel"

    mysql_setting_file = os.path.join(os.path.expanduser("~"),
                                     ".ipython/mysql_config.json")
    mysql_config = {
       "prompt"   : "mysql> ",
       "user"     : "root",
       "host"     : "127.0.0.1",
       "port"     : "3306",
       "charset"  : "utf8"
    }

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        if os.path.exists(self.mysql_setting_file):
            with open(self.mysql_setting_file,"r") as f:
                self.mysql_config.update(json.load(f))
        self.prompt = self.mysql_config["prompt"]
        self._start_process()
        self.table_names = []
        self.use_pat1 = re.compile(r"use\s+(?P<schema>[a-z0-9_]+)\s*;")
        self.use_pat2 = re.compile(r"\\u\s+(?P<schema>[a-z0-9_]+)\s*")
        self.schema_pat = re.compile(r"[a-z0-9_]+")
        self.tail_pat = re.compile(r"(.*?)(;|\\g|\\G)\s*$")
        self.select_pat = re.compile(r"^\s*select.*",flags=re.IGNORECASE)
        if "select_limit" in self.mysql_config:
            self.select_limit = int(self.mysql_config["select_limit"])
            self.select_limit_pat = re.compile(r".*?limit\s+\d+\s*$",flags=re.IGNORECASE) # NOTE: no ; or \g or \G

    def _start_process(self):
        # make childprocess interuptible by SIGINT
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            if "password" in self.mysql_config:
                self.ch = pexpect.spawn(
                        'mysql -A -h {host} -P {port} -u {user} -p'.format(**self.mysql_config))
            else:
                self.ch = pexpect.spawn(
                        'mysql -A -h {host} -P {port} -u {user}'.format(**self.mysql_config))
        finally:
            signal.signal(signal.SIGINT, sig)

        if self.ch.echo:
            self.ch.setecho(False)
            self.ch.waitnoecho()

        if "password" in self.mysql_config:
            self.ch.expect('Enter password: ')
            self.ch.sendline(self.mysql_config["password"])

        self.ch.expect(self.prompt)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        """Send SQL code to MySQL Commandline Tool via pexpect and get result
           If code is `use XXX;` reads table information for completion.
        """
        error_msg = []

        if not code.strip():
            return {'status': 'ok',
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {}}

        mes = ""
        for c in code.split("\n"):
            c = c.strip()
            if len(c) > 0:
                if c[0] == "#":
                    #skip comment
                    continue
                mes += c + " "
        mes = mes.strip()

        if mes[0] != "\\":
            mat = self.tail_pat.match(mes)
            if mat is None:
                tail = ";"
            else:
                mes = mat.group(1) # remove tail char
                tail = mat.group(2)

            # auto limit
            mat = self.select_pat.match(mes)
            if mat is not None and "select_limit" in self.mysql_config:
                mat = self.select_limit_pat.match(mes)
                if mat is None:
                    mes += " limit {}".format(self.select_limit)
                    error_msg.append("Auto select limit {}".format(self.select_limit))

            mes += tail # add tail char
            error_msg.append("{}".format(mes))

        # get table name for completion
        mat = self.use_pat1.match(mes.lower())
        if mat is None:
            mat = self.use_pat2.match(mes.lower())
        if mat is not None:
            schema_name = mat.group("schema")
            self.table_names = self._get_table_name(schema_name)

        interrupted = False
        try:
            self.ch.sendline(mes)
            self.ch.expect(self.prompt)
            output = self.ch.before
        except KeyboardInterrupt:
            self.ch.sendintr()
            self.ch.expect(self.prompt)
            interrupted = True
            output = self.ch.before
        except pexpect.EOF:
            output = self.ch.before + 'Restarting Process...'
            self._start_process()

        res = output.decode(self.mysql_config["charset"])
        # remove echo string
        # TODO: can't I disable echo?
        if res.find(mes) == 0:
            res = res[len(mes):]
        if res.find("> "+mes) == 0:
            res = res[len("> "+mes):]
        if tail == ";":
           pos = res.find("+")
           if pos > 0:
             res = res[pos:]

        if not silent:
            for e in error_msg[::-1]:
                res = e+"\n"+res
            stream_content = {'name': 'stdout', 'text': res}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]

        default = {'matches': [], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}

        if not code or code[-1] == ' ':
            return default

        tokens = code.replace(';', ' ')\
                     .replace('\\g',' ')\
                     .replace('\\G',' ')\
                     .split()
        if not tokens:
            return default

        token = tokens[-1]
        start = cursor_pos - len(token)
        matches = [w for w in self.table_names if w.startswith(token.upper())]
        matches.extend([w for w in WORDS_LIST if w.startswith(token.upper())])
        if token.islower():
            matches = [m.lower() for m in matches]

        return {'matches': sorted(matches), 'cursor_start': start,
                'cursor_end': cursor_pos, 'metadata': dict(),
                'status': 'ok'}

    def _get_table_name(self, schema_name):
        """Get table name on the schema
        """
        schema_name = schema_name.strip().lower()
        if self.schema_pat.match(schema_name) == None:
            # invalid schema name
            return []

        # get all table name
        # query = """
        #     select distinct(table_name)
        #     from information_schema.columns
        #     where table_schema not in
        #     ('information_schema', 'performance_schema', 'mysql')\G
        #     """
        query = """
            select distinct(table_name)
            from information_schema.columns
            where table_schema = "{schema}"\G
            """.format(schema = schema_name)

        try:
            self.ch.sendline(query.replace('\n',' '))
            self.ch.expect(self.prompt)
        except KeyboardInterrupt:
            self.ch.sendintr()
            self.ch.expect(self.prompt)
            return []
        except pexpect.EOF:
            #XXX: error handling
            return []

        # parse output
        res = self.ch.before.decode(self.mysql_config["charset"])
        l = res.split('\n')
        i = 0
        table_names = []
        while i < len(l):
            if len(l[i]) > 0:
                if l[i][0] == '*':
                    i += 1
                    pos = l[i].find("table_name:")
                    if pos != -1:
                        #table_names.append(l[i][pos+len("table_name:"):].strip().upper())
                        table_names.append(l[i][pos+len("table_name:"):].strip())
            i += 1

        return sorted(table_names)


if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MySQLKernel)
