# Copyright (c) 2018 Science and Technology Facilities Council

# All rights reserved.

# Modifications made as part of the fparser project are distributed
# under the following license:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Test Fortran 2003 rule R201 : This file tests the support for one
or more program-units.

'''

import pytest
from fparser.two.Fortran2003 import NoMatchError
from fparser.api import get_reader
from fparser.two.Fortran2003 import Program

# Test single program units


def test_single(f2003_create):
    '''Test that a single program_unit can be parsed successfully.'''
    reader = get_reader('''\
      subroutine test()
      end subroutine
      ''')
    ast = Program(reader)
    assert "SUBROUTINE test\n" \
        "END SUBROUTINE" in str(ast)


@pytest.mark.xfail(reason="5 spaces causes the error exception to occur at "
                   "the end of the file")
def test_single2(f2003_create):
    '''Test that a single program_unit with 5 or more spaces at the start
    of the line reports an error on the correct (first) line

    '''
    reader = get_reader('''\
     subroutin test()
     end subroutine

      ''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("at line 1\n>>>      subroutin test()\n"
            in str(excinfo.value))


@pytest.mark.xfail(reason="5 spaces causes the error exception to occur at "
                   "the end of the file")
def test_single3(f2003_create):
    '''Test that a single program_unit with 5 or more spaces at the start
    of the line reports an error on the correct (second) line

    '''
    reader = get_reader('''\
     subroutine test()
     end subroutin

      ''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("at line 2\n>>>      end subroutin\n"
            in str(excinfo.value))


def test_single_error1(f2003_create):
    '''Test that a single program_unit with an error in the initial
    statement raises an appropriate exception

    '''
    reader = get_reader('''\
      subroutin test()
      end subroutine
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("at line 1\n>>>      subroutin test()\n"
            in str(excinfo.value))


def test_single_error2(f2003_create):
    '''Test that a single program_unit with an error in the final
    statement raises an appropriate exception

    '''
    reader = get_reader(
        "subroutine test()\n\n"
        "end subroutin\n\n\n")
    with pytest.raises(NoMatchError) as excinfo:
        dummy = Program(reader)
    assert ("at line 3\n>>>end subroutin\n"
            in str(excinfo.value))

# Test multiple program units


def test_multiple(f2003_create):
    '''Test that multiple program_units can be parsed successfully.'''
    reader = get_reader('''\
      subroutine test()
      end subroutine
      subroutine test2()
      end subroutine test2
      ''')
    ast = Program(reader)
    assert "SUBROUTINE test\n" \
        "END SUBROUTINE" in str(ast)


@pytest.mark.xfail(reason="Having the same name in different program_units "
                   "does not raise an exception")
def test_multiple_error1(f2003_create):
    '''Test that multiple program_units with the same name raise an
    exception

    '''
    reader = get_reader('''\
      subroutine test()
      end subroutine
      subroutine test()
      end subroutine
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("XXX"
            in str(excinfo.value))


def test_multiple_error2(f2003_create):
    '''Test that a single program_unit with an error raises an appropriate
    exception

    '''
    reader = get_reader('''\
      subroutine 1test()
      end subroutine
      subroutine test()
      end subroutine
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("at line 1\n>>>      subroutine 1test()\n"
            in str(excinfo.value))


def test_multiple_error3(f2003_create):
    '''Test that multiple program_units with an error raises an
    appropriate exception

    '''
    reader = get_reader('''\
      subroutine test()
      end subroutine
      subroutine test()
      end subroutin''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("at line 4\n>>>      end subroutin\n"
            in str(excinfo.value))

# Test a program unit with a missing program statement


def test_missing_prog(f2003_create):
    '''Test that a main program program_unit without a program declaration
    can be parsed successfully. This should not really be a test here,
    but this case is currently treated separately by the match method
    in Program.

    '''
    reader = get_reader('''\
      end
      ''')
    ast = Program(reader)
    assert "END PROGRAM" in str(ast)


@pytest.mark.xfail(reason="Only the main program is output")
def test_missing_prog_multi(f2003_create):
    '''Test that a main program program_unit without a program declaration
    can be parsed successfully when it is not the first program_unit.

    '''
    reader = get_reader('''\
      subroutine first
      end
      end
      ''')
    ast = Program(reader)
    assert "SUBROUTINE first\n" \
        "END SUBROUTINE" in str(ast)
    assert "END PROGRAM" in str(ast)

# A program should contain only only one main program


@pytest.mark.xfail(reason="Only one main program is allowed in a program")
def test_one_main1(f2003_create):
    '''Test that multiple main programs raise an exception.'''
    reader = get_reader('''\
      program first
      end
      program second
      end
      ''')
    with pytest.raises(NoMatchError) as excinfo:
        dummy_ = Program(reader)
    assert ("XXX"
            in str(excinfo.value))


# Check comments are supported at this level


def test_comment0(f2003_create):
    '''Test that a single program_unit without comments can be parsed
    successfully with comment processing switched on.

    '''
    reader = get_reader((
        "subroutine test()\n"
        "end subroutine\n"), ignore_comments=False)
    ast = Program(reader)
    assert ("SUBROUTINE test\n"
            "END SUBROUTINE test") in str(ast)


def test_comment1(f2003_create):
    '''Test that a single program_unit can be parsed successfully with
    comments being ignored.'''
    reader = get_reader('''\
      ! comment1
      subroutine test()
      end subroutine
      ! comment2
      ''')
    ast = Program(reader)
    assert "SUBROUTINE test\n" \
        "END SUBROUTINE" in str(ast)
    assert "! comment" not in str(ast)


def test_comment2(f2003_create):
    '''Test that a single program_unit can be parsed successfully with
    comments being included.'''
    reader = get_reader((
        "! comment1\n"
        "subroutine test()\n"
        "end subroutine\n"
        "! comment2\n"), ignore_comments=False)
    ast = Program(reader)
    assert ("! comment1\n"
            "SUBROUTINE test\n"
            "END SUBROUTINE test\n"
            "! comment2") in str(ast)


def test_comment3(f2003_create):
    '''Test that multiple program_units can be parsed successfully with
    comments being ignored.'''
    reader = get_reader('''\
      ! comment1
      subroutine test()
      end subroutine
      ! comment2
      module example
      end module
      ! comment3
      ''', ignore_comments=True)
    ast = Program(reader)
    assert ("SUBROUTINE test\n"
            "END SUBROUTINE test\n"
            "MODULE example\n"
            "END MODULE example") in str(ast)
    assert "! comment" not in str(ast)


def test_comment4(f2003_create):
    '''Test that multiple program_units can be parsed successfully with
    comments being included.'''
    reader = get_reader((
      "! comment1\n"
      "subroutine test()\n"
      "end subroutine\n"
      "! comment2\n"
      "module example\n"
      "end module\n"
      "! comment3\n"
      ), ignore_comments=False)
    ast = Program(reader)
    assert ("! comment1\n"
            "SUBROUTINE test\n"
            "END SUBROUTINE test\n"
            "! comment2\n"
            "MODULE example\n"
            "END MODULE example\n"
            "! comment3") in str(ast)
