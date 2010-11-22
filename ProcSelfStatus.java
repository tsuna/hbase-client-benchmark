/* Copyright 2010  Benoit Sigoure
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.  */
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;

final class ProcSelfStatus {
  public static String read() throws Exception {
    FileInputStream in;
    try {
      in = new FileInputStream("/proc/self/status");
    } catch (FileNotFoundException e) {
      return "/proc/self/status no available\n";
    }
    final byte[] buf = new byte[1024];
    in.read(buf);
    in.close();
    return new String(buf);
  }
  public static void main(String[] a) throws Exception {
    System.out.print(read());
  }
}
