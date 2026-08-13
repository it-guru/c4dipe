
import kernel.query.int
import kernel.query.SQL
import kernel.query.Static
import json

search_criteria = [ # Level 1 (AND)
  [ # Level 2 (OR)
    {"basefeld": "AusdruckA",
        "cpucount": ">4"
    },
    {"department": "IT", "role": "admin dev*"}
  ],
  [ # Level 2 (OR)
    {"ffeld": "Ausd*ruckA", 
     "name": "Egon",
     "nameneg": "!*Egon*",
     "mdate": ">10.03.1999 10:00:00"
    },
    {
        "address": 'Bamberg Koeln "A*"', 
        "street": "abc* cde?",
        "zipcode": ['1234', '5678', '7890'],# List of constants (=) with OR
        "cpucount": 4,
        "mdate": "10.03.1972 10:00:00"
    }
  ]
]

fieldmap={
   "mdate":{ "type":"Date" },
   "cpucount":{ "type":"Number" }
}


ast=kernel.query.int.build_ast(search_criteria,fieldmap)

print("iquery=%s" % json.dumps(search_criteria,indent=2))
print("astree=%s" % json.dumps(ast.to_dict(),indent=2))

c=kernel.query.SQL.Compiler()
wherestr,qparam=c.compile(ast)
print("where=%s" % wherestr)
print("qparam=%s" % json.dumps(qparam,indent=2))


m=kernel.query.Static.Compiler()
matcher=m.compile(ast)
print("Static matcher code=%s" % matcher.__source__)


