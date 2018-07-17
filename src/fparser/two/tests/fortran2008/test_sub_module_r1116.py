'''Test Fortran 2008 rule R1116 and its constraints C1112 and C1114

    submodule is submodule-stmt
                 [ specification-part ]
                 [ module-subprogram-part ]
                 end-submodule-stmt

    C1112 A submodule specification-part shall not contain a
    format-stmt, entry-stmt, or stmt-function-stmt.

    C1114 If a submodule-name appears in the end-submodule-stmt, it
    shall be identical to the one in the submodule-stmt.

'''

import pytest
from fparser.api import get_reader
from fparser.two.Fortran2003 import NoMatchError
from fparser.two.Fortran2008 import Sub_Module
from fparser.two.parser import ParserFactory
# this is required to setup the fortran2008 classes
_ = ParserFactory().create(std="f2008")


def test_submodule():
    '''Test the parsing of a minimal submodule'''
    reader = get_reader('''\
      submodule (foobar) bar
      end
      ''')
    ast = Sub_Module(reader)
    assert "SUBMODULE (foobar) bar\n" \
        "END SUBMODULE bar" in str(ast)


def test_submodule_sp():
    '''Test the parsing of a minimal submodule with a specification
    part

    '''
    reader = get_reader('''\
      submodule (foobar) bar
        use empty
      end
      ''')
    ast = Sub_Module(reader)
    assert "SUBMODULE (foobar) bar\n" \
        "  USE empty\n" \
        "END SUBMODULE bar" in str(ast)


def test_submodule_msp():
    '''Test the parsing of a minimal submodule with a module subprogram
    part

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      contains
        subroutine info()
        end subroutine info
      end
      ''')
    ast = Sub_Module(reader)
    assert "SUBMODULE (foobar) bar\n" \
        "  CONTAINS\n" \
        "  SUBROUTINE info\n" \
        "  END SUBROUTINE info\n" \
        "END SUBMODULE bar" in str(ast)


def test_submodule_both():
    '''Test the parsing of a minimal submodule with a specification part
    and a module subprogram part

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      use empty
      contains
        subroutine info()
        end subroutine info
      end
      ''')
    ast = Sub_Module(reader)
    assert "SUBMODULE (foobar) bar\n" \
        "  USE empty\n" \
        "  CONTAINS\n" \
        "  SUBROUTINE info\n" \
        "  END SUBROUTINE info\n" \
        "END SUBMODULE bar" in str(ast)

# constraint C1112 format statement


def test_submodule_format_error1():
    '''C1112: Test an exception is raised if a format statement is
    specified in a submodule. The first place it can occur is in the
    implicit part of the specification

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      1 format(a)
      end
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        _ = Sub_Module(reader)
    assert ("at line 2\n"
            ">>>      1 format(a)\n"
            in str(excinfo.value))


def test_submodule_format_error2():
    '''C1112: Test an exception is raised if a format statement is
    specified in a submodule. The second place it can occur is in the
    declaration part of the specification

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      contains
      1 format(a)
      end
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        _ = Sub_Module(reader)
    assert ("at line 3\n"
            ">>>      1 format(a)\n"
            in str(excinfo.value))

# constraint C1112 entry statement


def test_submodule_entry_error1():
    '''C1112: Test an exception is raised if an entry statement is
    specified in a submodule. The first place it can occur is in the
    implicit part of the specification

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      entry here
      end
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        _ = Sub_Module(reader)
    assert ("at line 2\n"
            ">>>      entry here\n"
            in str(excinfo.value))


def test_submodule_entry_error2():
    '''C1112: Test an exception is raised if an entry statement is
    specified in a submodule. The second place it can occur is in the
    declaration part of the specification

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      contains
      entry here
      end
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        _ = Sub_Module(reader)
    assert ("at line 3\n"
            ">>>      entry here\n"
            in str(excinfo.value))

# constraint C1112 statement-function statement


def test_submodule_stmt_func_error():
    '''C1112: Test an exception is raised if a statement-function
    statement is specified in a submodule. The only place it could
    validly occur is in the declaration part of the specification

    '''
    reader = get_reader('''\
      submodule (foobar) bar
      contains
      statefunc(x) = x*2
      end
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        _ = Sub_Module(reader)
    assert ("at line 3\n"
            ">>>      statefunc(x) = x*2\n"
            in str(excinfo.value))

# constraint C1114


def test_submodule_samename():
    '''Test the parsing of a submodule with the same name : C1114'''
    reader = get_reader('''\
      submodule (foobar) bar
      end submodule bar
      ''')
    ast = Sub_Module(reader)
    assert "SUBMODULE (foobar) bar\n" \
        "END SUBMODULE bar" in str(ast)


def test_submodule_differentname():
    '''Test and exception is raised if a submodule has a different name :
    C1114'''
    reader = get_reader('''\
      submodule (foobar) bar
      end submodule error
      ''')
    with pytest.raises(SystemExit):
        _ = Sub_Module(reader)
