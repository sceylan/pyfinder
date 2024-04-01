/*
 * <Wrapper for SC3 logging to match PLOG statements in FinDer library>
 * Copyright (C) <2022>  
 *      Jennifer Andrews, GNS Science, jen.andrews@gns.cri.nz
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the 
 * GNU General Public License as published by the Free Software Foundation, either version 3 of 
 * the License, or (at your option) any later version with the additional stipulation that you 
 * give proper reference when using or modifying this code.
 *
 * plog: https://github.com/SergiusTheBest/plog
 * seiscomp: 
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See 
 * the GNU General Public License for more details. You should have received a copy of the GNU 
 * General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * This software is preliminary or provisional and is subject to revision. It is being provided to 
 * meet the need for timely best science. This program is provided “as is”. GNS Science disclaims all 
 * warranties, including any implied warranties of merchantability or fitness for any purpose.
 */

#ifndef __plog2sclog_wrapper_h__
#define __plog2sclog_wrapper_h__

#define SEISCOMP_COMPONENT libFinDer

#include <seiscomp/logging/log.h>
#include <algorithm>
#include <sstream>

namespace sclogwrap {
enum Log_Level {
  ERROR,
  WARNING,
  INFO,
  DEBUG
}; // log level to pass to sclog

class Record {
  private:
    Log_Level m_severity;
    std::stringstream m_message;
    std::string m_ell;

  public:
    Record(Log_Level severity) : m_severity(severity) {
      m_ell = "ELL";
    }

    //Templated operator>> that uses the std::ostream: Everything that has defined
    //an operator<< for the std::ostream (Everithing "printable" with std::cout
    //and its colleages) can use this function.

    void sclog() {
        std::string str = m_message.str();
        str.erase(std::remove(str.begin(), str.end(), '\n'), str.end());
        switch(m_severity) {
          case 0:
            SEISCOMP_ERROR("%s",str.c_str());
            break;
          case 1:
            SEISCOMP_WARNING("%s",str.c_str());
            break;
          case 2:
            SEISCOMP_INFO("%s",str.c_str());
            break;
          case 3:
            SEISCOMP_DEBUG("%s",str.c_str());
            break;
          default:
            SEISCOMP_DEBUG("%s",str.c_str());
            break;
        }
        m_message.clear();
        m_message.str(std::string());
        return;
    }

    Record& operator<< (char data) {
        char str[] = { data, 0 };
        m_message << str;
        return *this;
    }

    Record& operator<< (std::ostream& (*data)(std::ostream&)) {
        m_message << data;
        return *this;
    }

    template<typename T>
    Record& operator<< (const T& data) {
        std::stringstream ss;
        ss << data;
        if (ss.str() == m_ell) {
            if (m_message.str().length() > 0) {
                sclog();
            }
        } else {
            m_message << ss.str();
        }
        return *this;
    }
}; // class Record
}

#define LOGF  sclogwrap::Record(sclogwrap::ERROR)
#define LOGE  sclogwrap::Record(sclogwrap::ERROR)
#define LOGW  sclogwrap::Record(sclogwrap::WARNING)
#define LOGI  sclogwrap::Record(sclogwrap::INFO)
#define LOGD  sclogwrap::Record(sclogwrap::DEBUG)
#define LOGV  sclogwrap::Record(sclogwrap::DEBUG)
#define LOGN  sclogwrap::Record(sclogwrap::DEBUG)

#endif // __plog2sclog_wrapper_h__

// end of file: sc2plog_wrapper.h
