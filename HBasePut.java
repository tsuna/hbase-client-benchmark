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
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;

final class HBasePut {
  public static void main(String[] a) throws Exception {
    final HTable htable = HTableFactory.get();
    final Put put = new Put("foo".getBytes());
    put.add("t".getBytes(), "qualifier".getBytes(), "value".getBytes());
    htable.put(put);
  }
}
